import os

import boto3
from boto3.dynamodb.conditions import Key

from common.responses import build_response

TABLE_NAME = os.environ["TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def handler(event, context):
    user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
    status = (event.get("queryStringParameters") or {}).get("status")

    if status:
        response = table.query(
            IndexName="StatusIndex",
            KeyConditionExpression=Key("UserId").eq(user_id) & Key("Status").eq(status),
        )
    else:
        response = table.query(KeyConditionExpression=Key("UserId").eq(user_id))

    return build_response(200, {"tasks": response.get("Items", [])})
