import logging
import os

import boto3
from botocore.exceptions import ClientError

from common.responses import build_response

TABLE_NAME = os.environ["TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
            logger.info("DeleteTask: task %s not found for user %s", task_id, user_id)
            return build_response(404, {"message": "Task not found"})
        raise

    return build_response(204, None)
