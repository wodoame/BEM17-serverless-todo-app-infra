import json
import os

import boto3

sns = boto3.client("sns")
TOPIC_ARN = os.environ["TOPIC_ARN"]


def handler(event, context):
    user_id = event["request"]["userAttributes"]["sub"]
    email = event["request"]["userAttributes"].get("email")

    if email:
        sns.subscribe(
            TopicArn=TOPIC_ARN,
            Protocol="email",
            Endpoint=email,
            Attributes={
                "FilterPolicy": json.dumps({"UserId": [user_id]}),
            },
        )

    return event
