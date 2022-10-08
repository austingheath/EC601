use std::collections::HashMap;

use reqwest::{header::HeaderMap};
use reqwest::Error;
use rocket::serde::json::Json;
use rocket::serde::DeserializeOwned;
use serde::{Deserialize, Serialize};

#[macro_use] extern crate rocket;

const TWITTER_URL: &str = "https://api.twitter.com/2";
const TWITTER_BEARER_TOKEN: &'static str = env!("TWITTER_BEARER_TOKEN", "$TWITTER_BEARER_TOKEN is not set");

const GOOGLE_NLP_URL: &'static str = "https://language.googleapis.com/v1";
const GOOGLE_NLP_BEARER_TOKEN: &'static str = env!("GOOGLE_NLP_BEARER_TOKEN", "$GOOGLE_NLP_BEARER_TOKEN is not set");

#[derive(Serialize, Deserialize, Debug)]
struct TwitterUser {
    id: String,
    username: String,
    name: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct TwitterTweet {
    id: String,
    text: String,
    edit_history_tweet_ids: Vec<String>,
}

#[derive(Serialize, Deserialize, Debug)]
struct TwitterResponse<TData> {
    data: TData,
}

#[derive(Serialize, Deserialize, Debug)]
struct NLPDocumentSentiment {
    magnitude: f32,
    score: f32,
}

#[derive(Serialize, Deserialize, Debug)]
struct NLPResponse {
    documentSentiment: NLPDocumentSentiment,
}

async fn make_twitter_get_request<TData:DeserializeOwned>(endpoint: &str) -> Result<TwitterResponse<TData>, Error> {
    let url = TWITTER_URL.to_owned() + endpoint;
    let bearer_token = "Bearer ".to_owned() + TWITTER_BEARER_TOKEN;

    // Setup headers
    let mut headers = HeaderMap::new();
    headers.insert("Authorization", bearer_token.parse().unwrap());

    // Make GET request
    let client = reqwest::Client::new();
    let result = client.get(url).headers(headers).send().await?.json::<TwitterResponse<TData>>().await;

    return result;
}

 async fn analyze_sentiment(text: &str) -> Result<NLPResponse, Error> {
    let url = GOOGLE_NLP_URL.to_owned() + "/documents:analyzeSentiment";
    let bearer_token = "Bearer ".to_owned() + GOOGLE_NLP_BEARER_TOKEN;

    // Setup headers
    let mut headers = HeaderMap::new();
    headers.insert("Content-Type", "application/json".parse().unwrap());
    headers.insert("Authorization", bearer_token.parse().unwrap());

    // Setup body
    let mut document = HashMap::new();
    document.insert("content", text);
    document.insert("type", "PLAIN_TEXT");

    let mut body = HashMap::new();
    body.insert("document", document);

    // Make GET request
    let client = reqwest::Client::new();
    let result = client.post(url).headers(headers).json(&body).send().await?.json::<NLPResponse>().await;

    return result;
}

#[get("/<id>")]
async fn tweet_sentiment(id: &str) -> Result<String, String> {
    let twitter_endpoint = "/tweets/".to_owned() + id; 
    let response = make_twitter_get_request::<TwitterTweet>(&twitter_endpoint).await;
    
    match response {
        Ok(tweet) => {
            let sentiment_response = analyze_sentiment(&tweet.data.text).await;
            
            match sentiment_response {
                Ok(sentiment) => Ok(sentiment.documentSentiment.score.to_string()),
                Err(e) => Err("Couldn't get sentiment".to_string())
            }
        },
        Err(e) => Err("Couldn't make twitter request".to_string())
    }
}


#[get("/<username>")]
async fn user_by_username(username: &str) -> Result<Json<TwitterResponse<TwitterUser>>, String> {
    let twitter_endpoint = "/users/by/username/".to_owned() + username; 
    let response = make_twitter_get_request::<TwitterUser>(&twitter_endpoint).await;
    
    match response {
        Ok(v) => Ok(Json(v)),
        Err(e) => Err("It went wrong".to_string())
    }
}

#[launch]
fn rocket() -> _ {
    rocket::build()
        .mount("/users", routes![user_by_username])
        .mount("/tweets", routes![tweet_sentiment])
}