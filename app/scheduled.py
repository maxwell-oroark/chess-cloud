import json
import time
import requests
import chess.pgn
from datetime import datetime, timedelta
from string import Template
from google.cloud import storage, tasks_v2

storage_client = storage.Client()
tasks_client = tasks_v2.CloudTasksClient()

last_hour_date_time = datetime.now() - timedelta(hours=1)
last_hour_unix = time.mktime(last_hour_date_time.timetuple())

pgns = requests.get(
    "https://lichess.org/api/games/user/moroark?max=5&pgnInJson=true",
    headers={"Accept": "application/x-ndjson"},
)


def write_game(game):
    bucket = storage_client.get_bucket("raw_games")
    blob = bucket.blob(f"{game['id']}.pgn")
    blob.upload_from_string(game["pgn"])
    print("file uploaded")


def create_task(game):
    project = "chess-365123"
    queue = "games"
    location = "us-central1"
    url = "https://chess-zpmjyzr74q-uc.a.run.app/"
    payload = {"id": game["id"]}
    task_name = None

    parent = tasks_client.queue_path(project, location, queue)
    task = {
        "http_request": {  # Specify the type of request.
            "http_method": tasks_v2.HttpMethod.POST,
            "headers": {"Content-type": "application/json"},
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
        task["name"] = tasks_client.task_path(project, location, queue, task_name)

    response = tasks_client.create_task(request={"parent": parent, "task": task})
    print("Created task {}".format(response.name))


with open("/tmp/games.pgn", "w") as f:
    f.write(pgns.text)

with open("/tmp/games.pgn", "r") as f:
    delimiter = "\n"
    games = [x for x in f.read().split(delimiter) if x]
    for game in games:
        game = json.loads(game)
        write_game(game)
        create_task(game)

    print("script executed successfully")
