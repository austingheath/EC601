use std::collections::HashMap;

use reqwest::header::HeaderMap;
use serde::{Deserialize, Serialize};

const GOOGLE_NLP_URL: &'static str = "https://language.googleapis.com/v1";
const GOOGLE_NLP_BEARER_TOKEN: &'static str = env!(
    "GOOGLE_NLP_BEARER_TOKEN",
    "$GOOGLE_NLP_BEARER_TOKEN is not set"
);

#[derive(Serialize, Deserialize, Debug)]
struct NLPDocumentSentiment {
    magnitude: f32,
    score: f32,
}

#[allow(non_snake_case)]
#[derive(Serialize, Deserialize, Debug)]
struct NLPResponse {
    documentSentiment: NLPDocumentSentiment,
}

pub async fn analyze_sentiment(text: &str) -> Result<f32, String> {
    let url = GOOGLE_NLP_URL.to_owned() + "/documents:analyzeSentiment";

    // Setup headers
    let mut headers = HeaderMap::new();
    headers.insert("Content-Type", "application/json".parse().unwrap());

    // Setup query params
    let url_query_params = [("key", GOOGLE_NLP_BEARER_TOKEN)];

    // Setup body
    let mut document = HashMap::new();
    document.insert("content", text);
    document.insert("type", "PLAIN_TEXT");

    let mut body = HashMap::new();
    body.insert("document", document);

    // Make GET request
    let client = reqwest::Client::new();
    let response = client
        .post(url)
        .headers(headers)
        .query(&url_query_params)
        .json(&body)
        .send()
        .await
        .unwrap();

    match response.status() {
        reqwest::StatusCode::OK => match response.json::<NLPResponse>().await {
            Ok(parsed) => Ok(parsed.documentSentiment.score),
            Err(e) => Err(e.to_string()),
        },
        reqwest::StatusCode::UNAUTHORIZED => Err("Unauthorized call to Google NLP.".to_string()),
        other => Err(format!("Unexpected status code {}", other)),
    }
}
