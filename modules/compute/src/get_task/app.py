import os

import boto3

from common.responses import build_response

TABLE_NAME = os.environ["TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def handler(event, context):
    user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
    task_id = event["pathParameters"]["taskId"]

    response = table.get_item(Key={"UserId": user_id, "TaskId": task_id})
    item = response.get("Item")

    if not item:
        return build_response(404, {"message": "Task not found"})

    return build_response(200, item)
