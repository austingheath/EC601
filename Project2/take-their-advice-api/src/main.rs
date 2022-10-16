use futures::StreamExt;
use std::sync::Arc;
use std::{collections::HashMap, convert::Infallible};
use take_their_advice_api::twitter;
use take_their_advice_api::{controllers, ws::connection::Clients};
use tokio::sync::RwLock;
use warp::Filter;

#[tokio::main]
async fn main() {
    let clients: Clients = Arc::new(RwLock::new(HashMap::new()));

    let health_route = warp::path("health").and_then(controllers::health_handler);

    let ws_route = warp::path("ws")
        .and(warp::ws())
        .and(with_clients(clients.clone()))
        .and_then(controllers::ws_handler);

    let routes = warp::path("api")
        .and(health_route.or(ws_route))
        .with(warp::cors().allow_any_origin());

    let t1 = tokio::task::spawn(stream_tweets(clients));
    let t2 = tokio::task::spawn(warp::serve(routes).run(([127, 0, 0, 1], 8000)));

    (t1.await.unwrap(), t2.await.unwrap());
}

fn with_clients(clients: Clients) -> impl Filter<Extract = (Clients,), Error = Infallible> + Clone {
    warp::any().map(move || clients.clone())
}

async fn stream_tweets(clients: Clients) {
    println!("Starting tweet watch thread");

    // Block until there is a client that is watching a user
    'outer: loop {
        for (_, value) in clients.read().await.iter() {
            if let Some(_) = &value.streaming_user_info {
                break 'outer;
            }
        }
    }

    println!("Done blocking. Starting to stream tweets.");

    // Start streaming tweets
    let stream_res = twitter::requests::stream("/tweets/search/stream/rules".to_string()).await;

    let mut stream = match stream_res {
        Ok(r) => r,
        Err(e) => {
            println!("Could not setup stream {}", e.error);
            return;
        }
    };

    while let Some(item) = stream.next().await {
        println!("Chunk: {:?}", item);
    }
}
