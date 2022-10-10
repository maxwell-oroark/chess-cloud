"""Create a task for a given queue with an arbitrary payload."""

from google.cloud import tasks_v2

# Create a client.
client = tasks_v2.CloudTasksClient()

# TODO(developer): Uncomment these lines and replace with your values.
project = "chess-crunch"
queue = "hello-queue"
location = "us-central1"
url = "https://hello-3jdg5ibyua-uc.a.run.app"
audience = "https://hello-3jdg5ibyua-uc.a.run.app"
service_account_email = (
    "my-invoker-service-account@chess-crunch.iam.gserviceaccount.com"
)
payload = "hellogggg"

# Construct the fully qualified queue name.
parent = client.queue_path(project, location, queue)

# Construct the request body.
task = {
    "http_request": {  # Specify the type of request.
        "http_method": tasks_v2.HttpMethod.POST,
        "url": url,  # The full url path that the task will be sent to.
        "oidc_token": {
            "service_account_email": service_account_email,
        },
    }
}

if payload is not None:
    # The API expects a payload of type bytes.
    converted_payload = payload.encode()

    # Add the payload to the request.
    task["http_request"]["body"] = converted_payload

# Use the client to build and send the task.
response = client.create_task(request={"parent": parent, "task": task})

print("Created task {}".format(response.name))
# return response
