import os

import boto3
from botocore.exceptions import ClientError

from common.responses import build_response

TABLE_NAME = os.environ["TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def handler(event, context):
    user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
    task_id = event["pathParameters"]["taskId"]

    try:
        table.delete_item(
            Key={"UserId": user_id, "TaskId": task_id},
            ConditionExpression="attribute_exists(TaskId)",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return build_response(404, {"message": "Task not found"})
        raise

    return build_response(204, None)
