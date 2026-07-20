import json
import os

import boto3

sqs = boto3.client("sqs")
QUEUE_URL = os.environ["QUEUE_URL"]

CANCELABLE_NEW_STATUSES = {"Completed"}


def handler(event, context):
    for record in event.get("Records", []):
        cancellation = _cancellation_reason(record)
        if not cancellation:
            continue

        old_image = record["dynamodb"]["OldImage"]
        task_id = old_image["TaskId"]["S"]
        user_id = old_image["UserId"]["S"]

        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({"TaskId": task_id, "UserId": user_id, "Reason": cancellation}),
            MessageGroupId=task_id,
            MessageDeduplicationId=f"{task_id}-{cancellation}",
        )


def _cancellation_reason(record):
    old_image = record["dynamodb"].get("OldImage", {})
    if old_image.get("Status", {}).get("S") != "Pending":
        return None

    event_name = record["eventName"]
    if event_name == "REMOVE":
        return "Deleted"

    if event_name == "MODIFY":
        new_image = record["dynamodb"].get("NewImage", {})
        if new_image.get("Status", {}).get("S") in CANCELABLE_NEW_STATUSES:
            return "Completed"

    return None
