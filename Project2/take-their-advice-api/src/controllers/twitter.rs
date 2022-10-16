use crate::{
    controllers::common::{ApiErrorResponse, ApiJsonResult, ApiResponse},
    twitter::requests::{self, TwitterApiError, TwitterResponse, TwitterUser},
};
use rocket::{get, http::Status, serde::json::Json};

#[get("/twitter/users/<username>")]
pub async fn user_by_username(username: &str) -> ApiResponse<TwitterUser> {
    let twitter_endpoint = "/users/by/username/".to_owned() + username;
    let response = requests::get::<TwitterUser>(&twitter_endpoint).await;

    match response {
        Ok(t_res) => match t_res {
            TwitterResponse::Valid(res) => ApiResponse {
                json: Json(ApiJsonResult::Ok(res.data)),
                status: Status::Ok,
            },
            TwitterResponse::Error(err) => {
                if err.errors.len() == 0 {
                    return ApiResponse {
                        json: Json(ApiJsonResult::Error(ApiErrorResponse {
                            status: 400,
                            message: "Unknown twitter error".to_string(),
                        })),
                        status: Status::BadRequest,
                    };
                }

                let twitter_err = &err.errors[0];

                match twitter_err {
                    TwitterApiError::Type1(err) => ApiResponse {
                        json: Json(ApiJsonResult::Error(ApiErrorResponse {
                            status: 400,
                            message: err.detail.clone(),
                        })),
                        status: Status::BadRequest,
                    },
                    TwitterApiError::Type2(err) => ApiResponse {
                        json: Json(ApiJsonResult::Error(ApiErrorResponse {
                            status: 400,
                            message: err.message.clone(),
                        })),
                        status: Status::BadRequest,
                    },
                }
            }
        },
        Err(e) => ApiResponse {
            json: Json(ApiJsonResult::Error(ApiErrorResponse {
                status: e.status_code,
                message: e.error,
            })),
            status: Status::BadRequest,
        },
    }
}
