use futures::{FutureExt, StreamExt};
use tokio::sync::mpsc::{self};
use tokio_stream::wrappers::UnboundedReceiverStream;
use uuid::Uuid;
use warp::ws::WebSocket;

use std::collections::HashMap;

use std::sync::Arc;
use tokio::sync::RwLock;
use warp::ws::Message;

use crate::ws::processing::client_msg;

pub type Clients = Arc<RwLock<HashMap<String, Client>>>;

#[derive(Debug, Clone)]
pub struct Client {
    pub topics: Vec<String>,
    pub sender: mpsc::UnboundedSender<std::result::Result<Message, warp::Error>>,
}

pub async fn client_connection(ws: WebSocket, clients: Clients) {
    let (client_ws_sender, mut client_ws_rcv) = ws.split();
    let (client_sender, client_rcv) = mpsc::unbounded_channel();

    let client_rcv = UnboundedReceiverStream::new(client_rcv);
    tokio::task::spawn(client_rcv.forward(client_ws_sender).map(|result| {
        if let Err(e) = result {
            eprintln!("Error sending websocket msg: {}", e);
        }
    }));

    let uuid = Uuid::new_v4().as_simple().to_string();
    clients.write().await.insert(
        uuid.clone(),
        Client {
            topics: vec![],
            sender: client_sender,
        },
    );

    println!("{} connected", uuid);

    while let Some(result) = client_ws_rcv.next().await {
        let msg = match result {
            Ok(msg) => msg,
            Err(e) => {
                eprintln!(
                    "Error receiving ws message for id: {}): {}",
                    uuid.clone(),
                    e
                );
                break;
            }
        };
        client_msg(&uuid, msg, &clients).await;
    }

    clients.write().await.remove(&uuid);

    println!("{} disconnected", uuid);
}
