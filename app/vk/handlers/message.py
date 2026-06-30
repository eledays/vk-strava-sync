def handle_message(message: dict):
    text = message["text"].lower()
    user_id = message["from_id"]

    print(user_id, text)