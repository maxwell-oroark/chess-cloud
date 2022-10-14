"""Create a task for a given queue with an arbitrary payload."""
import sys
import datetime
import json

from google.cloud import tasks_v2, storage

# Create a client.
client = tasks_v2.CloudTasksClient()

project = "chess-365123"
queue = "games"
location = "us-central1"
url = "https://chess-zpmjyzr74q-uc.a.run.app/"
payload = {"pgn_file_name": "my-unique-id.pgn"}
task_name = "analyze-game-9"

# Construct the fully qualified queue name.
parent = client.queue_path(project, location, queue)

# Construct the request body.
task = {
    "http_request": {  # Specify the type of request.
        "http_method": tasks_v2.HttpMethod.POST,
        "url": url,  # The full url path that the task will be sent to.
    }
}
if payload is not None:
    if isinstance(payload, dict):
        # Convert dict to JSON string
        payload = json.dumps(payload)
        # specify http content-type to application/json
        task["http_request"]["headers"] = {"Content-type": "application/json"}

    # The API expects a payload of type bytes.
    converted_payload = payload.encode()

    # Add the payload to the request.
    task["http_request"]["body"] = converted_payload

if task_name is not None:
    # Add the name to tasks.
    task["name"] = client.task_path(project, location, queue, task_name)

# Use the client to build and send the task.
response = client.create_task(request={"parent": parent, "task": task})

print("Created task {}".format(response.name))
