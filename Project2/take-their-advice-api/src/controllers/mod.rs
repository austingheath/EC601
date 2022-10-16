use warp::{http::StatusCode, Rejection, Reply};

use crate::ws::connection::{client_connection, Clients};

pub async fn ws_handler(ws: warp::ws::Ws, clients: Clients) -> Result<impl Reply, Rejection> {
    Ok(ws.on_upgrade(move |socket| client_connection(socket, clients)))
}

pub async fn health_handler() -> Result<impl Reply, Rejection> {
    Ok(StatusCode::NO_CONTENT)
}
