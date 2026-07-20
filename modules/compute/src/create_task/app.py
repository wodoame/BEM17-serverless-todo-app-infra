import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import boto3

from common.responses import build_response

TABLE_NAME = os.environ["TABLE_NAME"]
DEFAULT_EXPIRY_MINUTES = int(os.environ.get("DEFAULT_EXPIRY_MINUTES", "5"))
SCHEDULE_GROUP_NAME = os.environ["SCHEDULE_GROUP_NAME"]
SCHEDULER_ROLE_ARN = os.environ["SCHEDULER_ROLE_ARN"]
EXPIRY_FUNCTION_ARN = os.environ["EXPIRY_FUNCTION_ARN"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
scheduler = boto3.client("scheduler")


def handler(event, context):
    user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
    body = json.loads(event.get("body") or "{}")

    description = body.get("Description")
    if not description:
        return build_response(400, {"message": "Description is required"})

    now = datetime.now(timezone.utc)
    deadline = now + timedelta(minutes=DEFAULT_EXPIRY_MINUTES)
    task_id = str(uuid.uuid4())

    task = {
        "UserId": user_id,
        "TaskId": task_id,
        "Description": description,
        "Date": body.get("Date"),
        "Status": "Pending",
        "Deadline": deadline.isoformat(),
        "CreatedAt": now.isoformat(),
    }

    table.put_item(Item=task)

    scheduler.create_schedule(
        Name=f"task-{task_id}",
        GroupName=SCHEDULE_GROUP_NAME,
        ScheduleExpression=f"at({deadline.strftime('%Y-%m-%dT%H:%M:%S')})",
        FlexibleTimeWindow={"Mode": "OFF"},
        ActionAfterCompletion="DELETE",
        Target={
            "Arn": EXPIRY_FUNCTION_ARN,
            "RoleArn": SCHEDULER_ROLE_ARN,
            "Input": json.dumps({"TaskId": task_id, "UserId": user_id}),
        },
    )

    return build_response(201, task)
