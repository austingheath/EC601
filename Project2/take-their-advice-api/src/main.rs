use reqwest::header::HeaderMap;

#[macro_use] extern crate rocket;

const TWITTER_BEARER_TOKEN: &str = "NOT INCLUDED";
const TWITTER_URL: &str = "https://api.twitter.com/2";

const NLP_URL: &str = "https://language.googleapis.com/v1";

#[tokio::main]
async fn make_twitter_get_request(endpoint: &str) -> Result<String, Box<dyn std::error::Error>> {
    let url = TWITTER_URL.to_owned() + endpoint;
    let bearer_token = "Bearer".to_owned() + TWITTER_BEARER_TOKEN;

    // Setup headers
    let mut headers = HeaderMap::new();
    headers.insert("Authorization", bearer_token.parse().unwrap());

    // Make GET request
    let client = reqwest::Client::new();
    let body = client.get(url).headers(headers).send().await?.text().await?;

    Ok(body)
}

#[tokio::main]
async fn analyze_sentiment(text: &str) -> Result<String, Box<dyn std::error::Error>> {
    let url = NLP_URL.to_owned() + "/documents:analyzeSentiment";

    // Setup headers
    // let mut headers = HeaderMap::new();
    // headers.insert("Authorization", bearer_token.parse().unwrap());

    // Setup body
    

    // Make GET request
    let client = reqwest::Client::new();
    let body = client.get(url).send().await?.text().await?;

    Ok(body)
}

#[get("/users/<username>")]
async fn users(username: &str) -> Result<String, String> {
    let endpoint = "/users/by/username/".to_owned() + username;
    let response = make_twitter_get_request(&endpoint);
    
    match response {
        Ok(v) => Ok(v),
        Err(e) => Err("It went wrong".to_string())
    }
}

#[launch]
fn rocket() -> _ {
    rocket::build()
        .mount("/users", routes![users])
}