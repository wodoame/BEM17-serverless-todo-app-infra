import os

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ["TABLE_NAME"]
TOPIC_ARN = os.environ["TOPIC_ARN"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
sns = boto3.client("sns")


def handler(event, context):
    user_id = event["UserId"]
    task_id = event["TaskId"]

    try:
        response = table.update_item(
            Key={"UserId": user_id, "TaskId": task_id},
            UpdateExpression="SET #status = :expired",
            ConditionExpression="attribute_exists(TaskId) AND #status = :pending",
            ExpressionAttributeNames={"#status": "Status"},
            ExpressionAttributeValues={":expired": "Expired", ":pending": "Pending"},
            ReturnValues="ALL_NEW",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return
        raise

    task = response["Attributes"]

    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject="Task expired",
        Message=f'Your task "{task.get("Description", task_id)}" has expired.',
        MessageAttributes={
            "UserId": {"DataType": "String", "StringValue": user_id},
        },
    )
