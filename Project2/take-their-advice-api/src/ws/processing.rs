use std::time::Duration;

use super::{
    connection::{self, Client, Clients},
    messages::{self, ClientMessage, ClientMessageData, ServerMessage},
};
use futures::StreamExt;
use serde_json::from_str;
use tokio::{sync::mpsc::UnboundedSender, time};
use uuid::Uuid;
use warp::{ws::Message, Error};

use crate::{
    google,
    twitter::{
        self,
        requests::{
            TwitterModifyTweetStreamRequest, TwitterResponse, TwitterTweetStreamAddRule,
            TwitterTweetStreamRule, TwitterTweetWithAuthor, TwitterUser,
        },
    },
    ws::{
        connection::StreamingUserInfo,
        messages::{SentimentMeasurement, ServerError, ServerMessageData},
    },
};

pub async fn client_msg(id: &str, msg: Message, clients: &connection::Clients) {
    println!("Received message from {}: {:?}", id, msg);

    let client = match clients.read().await.get(id).cloned() {
        Some(c) => c,
        None => return,
    };

    let message = match msg.to_str() {
        Ok(v) => v,
        Err(_) => return,
    };

    let client_message: ClientMessage = match from_str(&message) {
        Ok(v) => v,
        Err(e) => {
            send_message(
                gen_server_err_response(e.to_string(), 400.to_string(), None),
                client.sender,
            );

            return;
        }
    };

    match client_message.data {
        ClientMessageData::Subscribe(request) => {
            let mut locked = clients.write().await;
            if let Some(v) = locked.get_mut(id) {
                v.topics = request.topics;
            }
        }
        ClientMessageData::FindUser(request) => {
            let endpoint = "/users/by/username/".to_string() + &request.username;
            let twitter_res = twitter::requests::get::<TwitterUser>(endpoint).await;

            match twitter_res {
                Ok(r) => send_message(
                    gen_server_response(
                        ServerMessageData::TwitterUser(r),
                        Some(client_message.reference_id),
                    ),
                    client.sender,
                ),
                Err(e) => send_message(
                    gen_server_err_response(
                        e.error,
                        e.status_code.to_string(),
                        Some(client_message.reference_id),
                    ),
                    client.sender,
                ),
            }
        }
        ClientMessageData::WatchTwitterUser(request) => {
            match client.streaming_user_info {
                Some(_) => {
                    send_message(
                        gen_server_err_response(
                            "This client is already watching a user".to_string(),
                            "400".to_string(),
                            Some(client_message.reference_id),
                        ),
                        client.sender,
                    );

                    return;
                }
                None => {}
            }

            // Make sure the user actually exists
            let user_endpoint = format!("/users/by/username/{}", request.username);
            let twitter_user_res = twitter::requests::get::<TwitterUser>(user_endpoint).await;

            let user = match twitter_user_res {
                Ok(res) => res,
                Err(e) => {
                    send_message(
                        gen_server_err_response(
                            e.error,
                            e.status_code.to_string(),
                            Some(client_message.reference_id),
                        ),
                        client.sender,
                    );

                    return;
                }
            };

            // Register the username rule
            let tag_name = format!("{}_{}", id, request.username);
            let endpoint = "/tweets/search/stream/rules".to_string();
            let body = TwitterModifyTweetStreamRequest {
                add: Some(
                    [TwitterTweetStreamAddRule {
                        tag: tag_name.clone(),
                        value: format!("from:{}", request.username),
                    }]
                    .to_vec(),
                ),
                delete: None,
            };

            let twitter_res = twitter::requests::post::<
                Vec<TwitterTweetStreamRule>,
                TwitterModifyTweetStreamRequest,
            >(endpoint, body)
            .await;

            let tag = match twitter_res {
                Ok(res) => match res.into_iter().find(|x| x.tag == tag_name) {
                    Some(tag) => tag,
                    None => {
                        send_message(
                            gen_server_err_response(
                                format!("Could not find the tag {}", tag_name.clone()),
                                500.to_string(),
                                Some(client_message.reference_id),
                            ),
                            client.sender,
                        );

                        return;
                    }
                },
                Err(e) => {
                    send_message(
                        gen_server_err_response(
                            e.error,
                            e.status_code.to_string(),
                            Some(client_message.reference_id),
                        ),
                        client.sender,
                    );

                    return;
                }
            };

            // Write watch to client
            let mut locked = clients.write().await;
            if let Some(v) = locked.get_mut(id) {
                v.streaming_user_info = Some(StreamingUserInfo {
                    user,
                    rule_id: tag.id.clone(),
                    tweet_queue: [].to_vec(),
                })
            }
        }
    }
}

pub async fn stream_tweets(clients: Clients) {
    println!("Starting tweet watch thread");

    // Block until there is a client that is watching a user
    'outer: loop {
        let cls = clients.read().await;
        for (_, value) in cls.iter() {
            if let Some(_) = &value.streaming_user_info {
                break 'outer;
            }
        }

        time::sleep(Duration::from_secs(1)).await;
    }

    println!("Done blocking. Starting to stream tweets.");

    // Start streaming tweets for all clients
    let stream_res =
        twitter::requests::stream("/tweets/search/stream?tweet.fields=author_id".to_string()).await;

    let mut stream = match stream_res {
        Ok(r) => r,
        Err(e) => {
            println!("Could not setup stream {}", e.error);
            return;
        }
    };

    while let Some(chunk) = stream.next().await {
        let str_data = match chunk {
            Ok(data) => match std::string::String::from_utf8(data.to_vec()) {
                Ok(st) => st,
                Err(e) => {
                    println!("Error parsing chunk: {}", e.to_string());
                    break;
                }
            },
            Err(e) => {
                println!("Error processing chunk: {}", e.to_string());
                break;
            }
        };

        let tweet = match serde_json::from_str::<TwitterResponse<TwitterTweetWithAuthor>>(&str_data)
        {
            Ok(t) => match t {
                TwitterResponse::Error(_) => {
                    println!("Can't parse got twitter error response on {}", str_data);
                    continue;
                }
                TwitterResponse::Valid(tw) => tw.data,
            },
            Err(e) => {
                println!("Can't parse {}, got error {}", str_data, e.to_string());
                continue;
            }
        };

        println!("Tweet parsed: {}", &tweet.author_id);

        // Search for a matching client
        let mut locked_clients = clients.write().await;
        let watching_client: Option<Client> = {
            for (_, value) in locked_clients.iter_mut() {
                if let Some(info) = &value.streaming_user_info {
                    if info.user.id.eq(&tweet.author_id) {
                        Some(value);
                        break;
                    }
                }
            }

            None
        };

        // If there is a matching client, process the tweet
        if let Some(client) = watching_client {
            // Stream tweet to client
            send_message(
                gen_server_response(ServerMessageData::FoundTweet(tweet.clone()), None),
                client.sender.clone(),
            );

            // Add tweet to queue for sentiment processing later
            if let Some(mut info) = client.streaming_user_info {
                info.tweet_queue.push(tweet.text);
            }
        }
    }
}

pub async fn sentiment_calculator(clients: Clients) {
    println!("Starting sentiment watch thread");

    let mut interval = time::interval(Duration::from_secs(60 * 60));
    loop {
        // Process sentiment within every 60 minutes
        interval.tick().await;

        // Search for clients with tweets to process
        for (_, value) in clients.write().await.iter_mut() {
            if let Some(info) = value.streaming_user_info.as_mut() {
                if info.tweet_queue.len() == 0 {
                    continue;
                }

                // Combine the text for the client
                let combined_text = info.tweet_queue.join(". ").clone();

                // Calculate sentiment for each client
                let s_result = google::nlp::analyze_sentiment(&combined_text).await;

                if let Ok(sentiment) = s_result {
                    // Send sentiment to client
                    send_message(
                        gen_server_response(
                            ServerMessageData::SentimentMeasurement(SentimentMeasurement {
                                current_sentiment: sentiment,
                            }),
                            None,
                        ),
                        value.sender.clone(),
                    );
                }

                // Clear the array
                info.tweet_queue.clear();
            }
        }
    }
}

struct JsonResponse {
    json: String,
}

fn gen_server_err_response(
    error: String,
    code: String,
    response_id: Option<String>,
) -> Result<JsonResponse, String> {
    let uuid = Uuid::new_v4().as_simple().to_string();

    let message = ServerMessage {
        reference_id: uuid.clone(),
        response_id: response_id,
        data: messages::ServerMessageData::Error(ServerError {
            message: error,
            code,
        }),
    };

    match serde_json::to_string(&message) {
        Ok(s) => Ok(JsonResponse { json: s }),
        Err(e) => Err(e.to_string()),
    }
}

fn gen_server_response(
    data: messages::ServerMessageData,
    response_id: Option<String>,
) -> Result<JsonResponse, String> {
    let uuid = Uuid::new_v4().as_simple().to_string();

    let message = ServerMessage {
        reference_id: uuid.clone(),
        response_id: response_id,
        data,
    };

    match serde_json::to_string(&message) {
        Ok(s) => Ok(JsonResponse { json: s }),
        Err(e) => Err(e.to_string()),
    }
}

fn send_message(
    message: Result<JsonResponse, String>,
    sender: UnboundedSender<Result<Message, Error>>,
) {
    let json_str = match message {
        Ok(s) => s.json,
        Err(e) => e,
    };

    if let Err(_disconnected) = sender.send(Ok(Message::text(json_str.clone()))) {
        // Tx disconnected. Nothing to do.
    }
}
