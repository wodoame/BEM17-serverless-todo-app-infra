import json
import os

import boto3
from botocore.exceptions import ClientError

scheduler = boto3.client("scheduler")
SCHEDULE_GROUP_NAME = os.environ["SCHEDULE_GROUP_NAME"]


def handler(event, context):
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        task_id = body["TaskId"]

        try:
            scheduler.delete_schedule(Name=f"task-{task_id}", GroupName=SCHEDULE_GROUP_NAME)
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceNotFoundException":
                raise
