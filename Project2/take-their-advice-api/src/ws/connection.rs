use futures::{FutureExt, StreamExt};
use tokio::sync::mpsc::{self};
use tokio_stream::wrappers::UnboundedReceiverStream;
use uuid::Uuid;
use warp::ws::WebSocket;

use std::collections::HashMap;

use std::sync::Arc;
use tokio::sync::RwLock;
use warp::ws::Message;

use crate::twitter;
use crate::twitter::requests::{
    TwitterModifyTweetStreamRequest, TwitterTweetStreamDelete, TwitterTweetStreamRule,
};
use crate::ws::processing::client_msg;

pub type Clients = Arc<RwLock<HashMap<String, Client>>>;

#[derive(Debug, Clone)]
pub struct StreamingUserInfo {
    pub username: String,
    pub rule_id: String,
}

#[derive(Debug, Clone)]
pub struct Client {
    pub topics: Vec<String>,
    pub sender: mpsc::UnboundedSender<std::result::Result<Message, warp::Error>>,
    pub streaming_user_info: Option<StreamingUserInfo>,
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
            streaming_user_info: None,
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

    // Remove any watched user
    let client = match clients.read().await.get(&uuid).cloned() {
        Some(c) => c,
        None => return,
    };

    if let Some(info) = client.streaming_user_info {
        let endpoint = "/tweets/search/stream/rules".to_string();
        let body = TwitterModifyTweetStreamRequest {
            add: [].to_vec(),
            delete: Some(TwitterTweetStreamDelete {
                ids: [info.rule_id].to_vec(),
            }),
        };

        let twitter_res = twitter::requests::post::<
            Vec<TwitterTweetStreamRule>,
            TwitterModifyTweetStreamRequest,
        >(endpoint, body)
        .await;

        // Do nothing with response
        match twitter_res {
            Err(_) => {}
            Ok(_) => {}
        }
    }

    clients.write().await.remove(&uuid);

    println!("{} disconnected", uuid);
}
