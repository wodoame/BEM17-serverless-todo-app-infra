def handler(event, context):
    event["response"]["autoConfirmUser"] = True

    if event["request"]["userAttributes"].get("email"):
        event["response"]["autoVerifyEmail"] = True

    return event
