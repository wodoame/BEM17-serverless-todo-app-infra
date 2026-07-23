import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

scheduler = boto3.client("scheduler")
SCHEDULE_GROUP_NAME = os.environ["SCHEDULE_GROUP_NAME"]

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        task_id = body["TaskId"]

        try:
            scheduler.delete_schedule(Name=f"task-{task_id}", GroupName=SCHEDULE_GROUP_NAME)
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceNotFoundException":
                raise
            logger.info("Schedule for task %s already deleted, nothing to cancel", task_id)
