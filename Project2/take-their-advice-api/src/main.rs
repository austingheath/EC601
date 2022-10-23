use std::sync::Arc;
use std::{collections::HashMap, convert::Infallible};
use take_their_advice_api::ws::processing::{sentiment_calculator, stream_tweets};
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

    let t1 = tokio::task::spawn(warp::serve(routes).run(([127, 0, 0, 1], 8000)));
    let t2 = tokio::task::spawn(stream_tweets(clients.clone()));
    let t3 = tokio::task::spawn(sentiment_calculator(clients.clone()));

    (t1.await.unwrap(), t2.await.unwrap(), t3.await.unwrap());
}

fn with_clients(clients: Clients) -> impl Filter<Extract = (Clients,), Error = Infallible> + Clone {
    warp::any().map(move || clients.clone())
}
