import json
import requests
from datetime import datetime, timedelta
from google.cloud import storage, tasks_v2

storage_client = storage.Client()
tasks_client = tasks_v2.CloudTasksClient()

fifteen_minutes_ago = datetime.now() - timedelta(minutes=15)
fifteen_minutes_ago_ms = int(fifteen_minutes_ago.timestamp() * 1000)

users = ["moroark", "goroark"]


def new_game(game):
    bucket = storage_client.get_bucket("raw_games")
    blob = bucket.blob(f"{game['id']}.pgn")
    if blob.exists():
        return False
    return True


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
    payload = {
        "id": game["id"],
        "white_player": game["players"]["white"]["user"]["name"],
        "black_player": game["players"]["black"]["user"]["name"],
        "white_rating": game["players"]["white"]["rating"],
        "black_rating": game["players"]["black"]["rating"],
        "winner": game["winner"],
    }

    parent = tasks_client.queue_path(project, location, queue)
    task = {
        "http_request": {  # Specify the type of request.
            "http_method": tasks_v2.HttpMethod.POST,
            "headers": {"Content-type": "application/json"},
            "url": url,  # The full url path that the task will be sent to.
        }
    }
    # Convert dict to JSON string
    payload = json.dumps(payload)
    # specify http content-type to application/json
    task["http_request"]["headers"] = {"Content-type": "application/json"}

    # The API expects a payload of type bytes.
    converted_payload = payload.encode()

    # Add the payload to the request.
    task["http_request"]["body"] = converted_payload
    task["name"] = tasks_client.task_path(project, location, queue, game["id"])

    try:
        response = tasks_client.create_task(request={"parent": parent, "task": task})
        print("Created task {}".format(response.name))
    except Exception as e:
        print(e.message)


def query_games(data, context):
    games = ""
    for user in users:
        response = requests.get(
            f"https://lichess.org/api/games/user/{user}?pgnInJson=true&since={fifteen_minutes_ago_ms}",
            headers={"Accept": "application/x-ndjson"},
        )
        games += response.text

    with open("/tmp/games.ndjson", "w") as f:
        f.write(games)

    with open("/tmp/games.ndjson", "r") as f:
        delimiter = "\n"
        games = [x for x in f.read().split(delimiter) if x]
        print("GAMES:")
        print(len(games))
        print(games)
        if len(games) > 0:
            for game in games:
                game = json.loads(game)
                if new_game(game):
                    write_game(game)
                    create_task(game)

            print("script executed successfully")
        else:
            print("no new games to analyze")


if __name__ == "__main__":
    print(
        f"https://lichess.org/api/games/user/moroark?pgnInJson=true&since={fifteen_minutes_ago_ms}"
    )
    print(fifteen_minutes_ago_ms)
