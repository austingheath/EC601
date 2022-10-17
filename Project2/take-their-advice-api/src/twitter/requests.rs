use futures::Stream;
use reqwest::{header::HeaderMap, Response};
use serde::{de::DeserializeOwned, Deserialize, Serialize};

const TWITTER_URL: &str = "https://api.twitter.com/2";
const TWITTER_BEARER_TOKEN: &'static str =
    env!("TWITTER_BEARER_TOKEN", "$TWITTER_BEARER_TOKEN is not set");

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(rename_all = "camelCase")]
pub struct TwitterUser {
    pub id: String,
    pub username: String,
    pub name: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TwitterTweet {
    pub id: String,
    pub text: String,
    pub edit_history_tweet_ids: Vec<String>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct TwitterTweetWithAuthor {
    pub id: String,
    pub text: String,
    pub edit_history_tweet_ids: Vec<String>,
    pub author_id: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct TwitterTweetStreamAddRule {
    pub value: String,
    pub tag: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TwitterTweetStreamDelete {
    pub ids: Vec<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TwitterModifyTweetStreamRequest {
    pub add: Option<Vec<TwitterTweetStreamAddRule>>,
    pub delete: Option<TwitterTweetStreamDelete>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TwitterTweetStreamRule {
    pub value: String,
    pub tag: String,
    pub id: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ErrorResponse {
    pub error: String,
    pub status_code: u16,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TwitterApiType1Error {
    pub detail: Option<String>,
    pub title: String,
    pub r#type: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TwitterApiType2Error {
    pub message: String,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(untagged)]
pub enum TwitterApiError {
    Type1(TwitterApiType1Error),
    Type2(TwitterApiType2Error),
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TwitterApiInvalidResponse {
    pub errors: Vec<TwitterApiError>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct TwitterApiValidResponse<TResponse> {
    pub data: TResponse,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(untagged)]
pub enum TwitterResponse<TResponse> {
    Error(TwitterApiInvalidResponse),
    Valid(TwitterApiValidResponse<TResponse>),
}

pub async fn get<TResponse: DeserializeOwned>(
    endpoint: String,
) -> Result<TResponse, ErrorResponse> {
    let url = TWITTER_URL.to_owned() + &endpoint;

    // Make request
    let client = reqwest::Client::new();
    let response = client
        .get(url)
        .headers(prepare_headers())
        .send()
        .await
        .unwrap();

    process_reponse(response).await
}

pub async fn post<TResponse: DeserializeOwned, TBody: Serialize>(
    endpoint: String,
    body: TBody,
) -> Result<TResponse, ErrorResponse> {
    let url = TWITTER_URL.to_owned() + &endpoint;

    // Make request
    let client = reqwest::Client::new();
    let response = client
        .post(url)
        .json(&body)
        .headers(prepare_headers())
        .send()
        .await
        .unwrap();

    process_reponse(response).await
}

pub async fn stream(
    endpoint: String,
) -> Result<impl Stream<Item = Result<warp::hyper::body::Bytes, reqwest::Error>>, ErrorResponse> {
    let url = TWITTER_URL.to_owned() + &endpoint;
    let client = reqwest::Client::new();

    let result = client.get(url).headers(prepare_headers()).send().await;

    match result {
        Ok(s) => Ok(s.bytes_stream()),
        Err(e) => Err(ErrorResponse {
            error: e.to_string(),
            status_code: reqwest::StatusCode::INTERNAL_SERVER_ERROR.as_u16(),
        }),
    }
}

fn prepare_headers() -> HeaderMap {
    let bearer_token = "Bearer ".to_owned() + TWITTER_BEARER_TOKEN;

    let mut headers = HeaderMap::new();
    headers.insert("Authorization", bearer_token.parse().unwrap());

    headers
}

async fn process_reponse<TResponse: DeserializeOwned>(
    response: Response,
) -> Result<TResponse, ErrorResponse> {
    match response.status() {
        reqwest::StatusCode::BAD_REQUEST
        | reqwest::StatusCode::OK
        | reqwest::StatusCode::CREATED => {
            let res_text = response.text().await;

            let text = match res_text {
                Ok(text) => text,
                Err(e) => {
                    return Err(ErrorResponse {
                        error: e.to_string(),
                        status_code: reqwest::StatusCode::INTERNAL_SERVER_ERROR.as_u16(),
                    })
                }
            };

            match serde_json::from_str::<TwitterResponse<TResponse>>(&text) {
                Ok(parsed) => match parsed {
                    TwitterResponse::Valid(res) => Ok(res.data),
                    TwitterResponse::Error(e) => {
                        if e.errors.len() == 0 {
                            return Err(ErrorResponse {
                                error: "An unknown twitter error occurred".to_string(),
                                status_code: reqwest::StatusCode::INTERNAL_SERVER_ERROR.as_u16(),
                            });
                        }

                        let first_err = &e.errors[0];

                        let message = match first_err {
                            TwitterApiError::Type1(e) => &e.title,
                            TwitterApiError::Type2(e) => &e.message,
                        };

                        Err(ErrorResponse {
                            error: message.to_string(),
                            status_code: reqwest::StatusCode::BAD_REQUEST.as_u16(),
                        })
                    }
                },
                Err(_) => {
                    println!("Couldn't parse {} to result", text);
                    Err(ErrorResponse {
                        error: format!("Couldn't parse {} to result", text),
                        status_code: reqwest::StatusCode::INTERNAL_SERVER_ERROR.as_u16(),
                    })
                }
            }
        }
        reqwest::StatusCode::NOT_FOUND => Err(ErrorResponse {
            error: format!("Not found (404) call to Twitter API:{}", response.url()),
            status_code: response.status().as_u16(),
        }),
        reqwest::StatusCode::UNAUTHORIZED => Err(ErrorResponse {
            error: "Unauthorized (401) call to Twitter API.".to_string(),
            status_code: response.status().as_u16(),
        }),
        status => Err(ErrorResponse {
            error: format!("Unexpected status code {}", status),
            status_code: response.status().as_u16(),
        }),
    }
}
