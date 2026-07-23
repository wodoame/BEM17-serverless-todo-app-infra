import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

from common.responses import build_response

TABLE_NAME = os.environ["TABLE_NAME"]
ALLOWED_STATUSES = {"Pending", "Completed", "Expired"}

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
    task_id = event["pathParameters"]["taskId"]
    body = json.loads(event.get("body") or "{}")

    updates = {}
    if "Description" in body:
        updates["Description"] = body["Description"]
    if "Date" in body:
        updates["Date"] = body["Date"]
    if "Status" in body:
        if body["Status"] not in ALLOWED_STATUSES:
            return build_response(400, {"message": "Invalid status"})
        updates["Status"] = body["Status"]

    if not updates:
        return build_response(400, {"message": "No updatable fields provided"})

    try:
        response = table.update_item(
            Key={"UserId": user_id, "TaskId": task_id},
            UpdateExpression="SET " + ", ".join(f"#{k} = :{k}" for k in updates),
            ExpressionAttributeNames={f"#{k}": k for k in updates},
            ExpressionAttributeValues={f":{k}": v for k, v in updates.items()},
            ConditionExpression="attribute_exists(TaskId)",
            ReturnValues="ALL_NEW",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            logger.info("UpdateTask: task %s not found for user %s", task_id, user_id)
            return build_response(404, {"message": "Task not found"})
        raise

    return build_response(200, response["Attributes"])
