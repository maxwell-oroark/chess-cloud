import threading
import chess
import chess.engine
import chess.pgn

from flask import Flask, request


def write_ascii_board(board):
    print("getting here?")
    # line below creates ascii file and appends to it.
    print(board, file=open("ascii.txt", "a"))


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
            {"move": move.uci(), "score": info.white().score(mate_score=10000)}
        )

    engine.quit()
    print("ANALYSIS")
    print(analysis)
    return analysis


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def process_job():
    pgn = open("../sample.pgn", "r")
    print("PGN:")
    print(pgn)
    game = chess.pgn.read_game(pgn)
    thread = threading.Thread(target=analyze_game, args=(game,))
    thread.start()
    return "processing job...", 200


if __name__ == "__main__":
    # process_job()
    app.run(debug=True, host="0.0.0.0")
