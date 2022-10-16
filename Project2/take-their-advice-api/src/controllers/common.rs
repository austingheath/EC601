use rocket::http::ContentType;
use rocket::request::Request;
use rocket::response;
use rocket::response::{Responder, Response};
use rocket::{http::Status, serde::json::Json};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct ApiErrorResponse {
    pub status: u16,
    pub message: String,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(untagged)]
pub enum ApiJsonResult<TResult> {
    Error(ApiErrorResponse),
    Ok(TResult),
}

#[derive(Debug)]
pub struct ApiResponse<TResult> {
    pub json: Json<ApiJsonResult<TResult>>,
    pub status: Status,
}

impl<'r, T: serde::Serialize> Responder<'r, 'static> for ApiResponse<T> {
    fn respond_to(self, req: &Request) -> response::Result<'static> {
        Response::build_from(self.json.respond_to(&req).unwrap())
            .status(self.status)
            .header(ContentType::JSON)
            .ok()
    }
}
