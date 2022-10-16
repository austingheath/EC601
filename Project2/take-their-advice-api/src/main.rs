use std::sync::Arc;
use std::{collections::HashMap, convert::Infallible};
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

    warp::serve(routes).run(([127, 0, 0, 1], 8000)).await;
}

fn with_clients(clients: Clients) -> impl Filter<Extract = (Clients,), Error = Infallible> + Clone {
    warp::any().map(move || clients.clone())
}
