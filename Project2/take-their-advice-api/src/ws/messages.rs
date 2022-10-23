use serde::{Deserialize, Serialize};

use crate::twitter::requests::{TwitterTweetWithAuthor, TwitterUser};

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ClientMessage {
    pub reference_id: String,
    pub data: ClientMessageData,
    pub response_id: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ServerMessage {
    pub reference_id: String,
    pub data: ServerMessageData,
    pub response_id: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "type")]
#[serde(rename_all = "camelCase")]
pub enum ClientMessageData {
    Subscribe(TopicsRequest),
    FindUser(FindTwitterUser),
    WatchTwitterUser(WatchTwitterUser),
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "type")]
#[serde(rename_all = "camelCase")]
pub enum ServerMessageData {
    Error(ServerError),
    TwitterUser(TwitterUser),
    FoundTweet(TwitterTweetWithAuthor),
    SentimentMeasurement(SentimentMeasurement),
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct TopicsRequest {
    pub topics: Vec<String>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct FindTwitterUser {
    pub username: String,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct WatchTwitterUser {
    pub username: String,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ServerError {
    pub message: String,
    pub code: String,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct SentimentMeasurement {
    pub current_sentiment: f32,
}
