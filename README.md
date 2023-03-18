# 🤖 Rasa Backend for Ibentau Chatbot

This is a backend implementation for a chatbot using the open-source machine learning framework Rasa.

## Running the backend
### Train the model

Download a pretrained model from the github artifacts and place it in the `models` folder.

Or 

To train the model, run the following command:

```bash
rasa train
```

### Run the action server

To start the actions server, run the following command in the root directory of the project:

```bash
rasa run actions
```

### Run the server

To start the backend server, run the following command in the root directory of the project:

```bash
export ACTION_SERVER=localhost
export ACTION_PORT=5055

rasa run --enable-api
```

This will start the server at http://localhost:5005.

## Usage

### Sending a message

To send a message to the chatbot, send a POST request to the `/webhooks/rest/webhook` endpoint with the following body:

```json
{
  "sender": "test",
  "message": "Hello"
}
```

The `sender` field is used to identify the user. The `message` field is the message that the user sent.

### Receiving a response

The response will be a JSON array with the following structure:

```json
[
  {
    "recipient_id": "test",
    "text": "Hello, how can I help you?"
  }
]
```

The `recipient_id` field is the same as the `sender` field in the request. The `text` field is the response from the chatbot.
