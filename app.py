import threading
from time import sleep

import chess
import chess.engine
from flask import Flask


def write_ascii_board(board):
    print("getting here?")
    print(board, file=open("ascii.txt", "a"))


def analyze_game(pgn):
    board = chess.Board()
    engine = chess.engine.SimpleEngine.popen_uci(
        "stockfish-10-linux/Linux/stockfish_10_x64"
    )
    sleep(10)
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Qh5")
    info = engine.analyse(board, chess.engine.Limit(time=0.1))["score"]
    board.push_san("Nc6")
    board.push_san("Bc4")
    board.push_san("Nf6")
    board.push_san("Qxf7")
    write_ascii_board(board)
    engine.quit()


app = Flask(__name__)


@app.route("/")
def process_job():
    print("hello")
    thread = threading.Thread(target=analyze_game, kwargs={"pgn": "some_long_pgn"})
    thread.start()
    return "processing job...", 200


if __name__ == "__main__":
    # process_job()
    app.run(debug=True, host="0.0.0.0")
