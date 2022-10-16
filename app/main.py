import io
import json
import chess
import chess.engine
import chess.pgn

from flask import Flask, request
from google.cloud import storage

storage_client = storage.Client()

app = Flask(__name__)


def get_pgn(filename):
    bucket = storage_client.get_bucket("raw_games")
    blob = bucket.blob(f"{filename}.pgn")
    blob.download_to_filename("/tmp/game.pgn")
    f = open("/tmp/game.pgn")
    return f


def write_results(game_id, results):
    try:
        """Uploads json to the bucket."""
        results_json = json.dumps(results)
        bucket = storage_client.get_bucket("analyzed_games")
        blob = bucket.blob(f"{game_id}.json")
        blob.upload_from_string(results_json)
        print("file uploaded")
    except Exception as e:
        print("something went wrong while attempting to write to GCS:")
        print(e.message)


def analyze_game(game):
    analysis = []
    # connect to stockfish binary
    engine = chess.engine.SimpleEngine.popen_uci(
        "../stockfish-10-linux/Linux/stockfish_10_x64"
    )
    # iterate through all moves, play them on a board and analyse them.
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
        info = engine.analyse(board, chess.engine.Limit(time=0.1))["score"]
        analysis.append(
            {"move": board.san(move), "score": info.white().score(mate_score=10000)}
        )

    engine.quit()
    return analysis


@app.route("/", methods=["POST"])
def process_job():
    body = request.json
    print("BODY:")
    print(body)
    game_id = body["id"]
    pgn = get_pgn(game_id)
    print("PGN:")
    print(pgn)
    game = chess.pgn.read_game(pgn)
    analysis = analyze_game(game)
    write_results(game_id, analysis)

    return "processed job", 200


if __name__ == "__main__":
    # process_job()
    app.run(debug=True, host="0.0.0.0")
