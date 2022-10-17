import json
import time
import requests
from datetime import datetime, timedelta
from google.cloud import storage, tasks_v2

storage_client = storage.Client()
tasks_client = tasks_v2.CloudTasksClient()

last_fifteen_time = datetime.now() - timedelta(minutes=15)
last_unix = time.mktime(last_fifteen_time.timetuple())
unix_ms = int(last_unix * 1000)


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
    task_name = game["id"]

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

    try:
        response = tasks_client.create_task(request={"parent": parent, "task": task})
        print("Created task {}".format(response.name))
    except Exception as e:
        print(e.message)


def query_games(data, context):
    pgns = requests.get(
        f"https://lichess.org/api/games/user/moroark?pgnInJson=true&since={unix_ms}",
        headers={"Accept": "application/x-ndjson"},
    )
    with open("/tmp/games.pgn", "w") as f:
        f.write(pgns.text)

    with open("/tmp/games.pgn", "r") as f:
        delimiter = "\n"
        games = [x for x in f.read().split(delimiter) if x]
        if len(games) > 0:
            for game in games:
                game = json.loads(game)
                write_game(game)
                create_task(game)

            print("script executed successfully")
        else:
            print("no new games to analyze")


if __name__ == "__main__":
    query_games()
