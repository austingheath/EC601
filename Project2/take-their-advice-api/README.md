# Take Their Advice API

## Disclaimer

Written in Rust so I can learn the language. Probably not the greatest Rust codebase.

## Project Phases

### Project 2 Phase 1

- Init project, get somewhat familiar with the language
- Setup an API route for frontend
- Make GET requests to Twitter API
- Make NLP sentiment request

## Project 2 Phase 2

- Create a WebSocket server
- Error handling of Twitter & NLP server
- Allow WebSocket clients to stream tweets from a particular user of their choice
- Run sentiment on the tweets as the arrive (bulking should be done in the future)

## Project 2 Additional Changes

- Run sentiment every hour on tweets that are grouped per client (this prevents the sentiment server from being overloaded)
- Smarter websocket API with better error handling

## Using the API

### Setup

- Download Rust for your computer [here](https://www.rust-lang.org/tools/install)
- Before building, add a `.cargo/config.toml` file to the root
  - See the `config.toml.example` file to provide the Twitter API and Google NLP keys
- Build with `cargo build`
- Run with `./target/debug/take-their-advice-api` or `./target/debug/take-their-advice-api.exe` on Windows

### Usage

- The API provides two routes: `/api/ws` and `api/health`
- Using POSTMAN, or any other client capable of WebSockets, connect to the `ws` route
- Clients send JSON messages to the server

A message to a client from the server or vice versa is formatted as such:

```
{
    "referenceId": "<string>",
    "data": <MessageData>,
    "responseId": <string>
}
```

The `responseId` is included if the message is intended to respond directly to an incoming message. The value is the `referenceId` of the message it is responding to.

Clients can send two (technically three, but not important for now) types of `MessageData`:

```
{
    "type": "findUser",
    "username": <string>
}
```

or

```
{
    "type": "watchTwitterUser",
    "username": <string>
}
```

The server can response with several `MessageData` types:

```
{
    "type": "error",
    "message": <string>
    "code": <string>
}
```

or

```
{
    "type": "foundUser",
    "id": <string>,
    "username": <string>,
}
```

or

```
{
    "type": "foundTweet",
    "id": <string>,
    "text": <string>,
    "editHistoryTweetIds: <string[]>,
    "authorId": <string>,
}
```

or

```
{
    "type": "sentimentMeasurement",
    "sentiment": <number>
}
```

### An example client might

- Open a `ws` connection
- Search for a user using the `findUser` command
- If a user isn't found, the server will tell you with an `error` message
- Once a user is found, watch the user with `watchTwitterUser`
- The server will start streaming new tweets to the client
- Every hour, the server will update the client on the sentiment of all the tweets caught within that hour
- Using this information, a client might make stock trading deisions or simple provide sentiment updates to a user
