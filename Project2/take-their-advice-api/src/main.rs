use rocket::{launch, routes};
use take_their_advice_api::controllers::twitter::user_by_username;
use take_their_advice_api::twitter::requests::TwitterResponse;
use take_their_advice_api::{
    google::nlp,
    twitter::requests::{self, TwitterTweet},
};

async fn tweet_sentiment(id: &str) -> Result<String, String> {
    let twitter_endpoint = "/tweets/".to_owned() + id;
    let response = requests::get::<TwitterTweet>(&twitter_endpoint).await;

    match response {
        Ok(parsed) => match parsed {
            TwitterResponse::Valid(tweet) => {
                let sentiment_response = nlp::analyze_sentiment(&tweet.data.text).await;

                match sentiment_response {
                    Ok(sentiment) => Ok(sentiment.to_string()),
                    Err(e) => Err(e),
                }
            }
            TwitterResponse::Error(e) => Err("error".to_string()),
        },
        Err(e) => Err(e.error),
    }
}

#[launch]
fn rocket() -> _ {
    rocket::build().mount("/api", routes![user_by_username])
}
