# Script
import json
import requests

def getMaia(fen):
    MAIA_PORT = 8001
    SERVER = f"http://127.0.0.1:{MAIA_PORT}"
    ROUTE = "/getMove"
    PARAMS = "?fen=" + fen

    response = requests.get(SERVER + ROUTE + PARAMS)
    return response.json()


def getStockfish(fen):
    STOCKFISH_PORT = 8002
    SERVER = f"http://127.0.0.1:{STOCKFISH_PORT}"
    ROUTE = "/getAnalysis"
    PARAMS = "?fen=" + fen

    response = requests.get(SERVER + ROUTE + PARAMS)
    return response.json()


def getEval(fen):
    STOCKFISH_PORT = 8002
    SERVER = f"http://127.0.0.1:{STOCKFISH_PORT}"
    ROUTE = "/getEval"
    PARAMS = "?fen=" + fen

    response = requests.get(SERVER + ROUTE + PARAMS)
    return response.json()


with open("data/random_fens.json") as f:
    fens = json.load(f)

predictions = []

for fen in fens:
    maia = getMaia(fen)
    # Saves keys - fen, maia-1100 and maia-1900
    predictions.append({
        "fen": fen,
        "maia-1100": maia["maia-1100"],
        "maia-1900": maia["maia-1900"]
    })

with open("data/maia_predictions.json", "w") as f:
    json.dump(predictions, f)