use serde::{Deserialize, Serialize};

use crate::twitter::requests::TwitterUser;

#[derive(Serialize, Deserialize, Debug)]
pub struct ClientMessage {
    pub reference_id: String,
    pub data: ClientMessageData,
    pub response_id: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ServerMessage {
    pub reference_id: String,
    pub data: ServerMessageData,
    pub response_id: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "type")]
pub enum ClientMessageData {
    Subscribe(TopicsRequest),
    FindUser(FindTwitterUser),
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "type")]
pub enum ServerMessageData {
    Error(ServerError),
    TwitterUser(TwitterUser),
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TopicsRequest {
    pub topics: Vec<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct FindTwitterUser {
    pub username: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ServerError {
    pub message: String,
    pub code: String,
}
