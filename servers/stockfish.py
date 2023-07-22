# flask --app stockfish.py --debug run -p 8002
# Think about combining the two routes into one for efficiency
import math
import re
from flask import Flask, request, jsonify
from subprocess import Popen, PIPE
from atexit import register

app = Flask(__name__)
stockfish = Popen(
    ['stockfish'], stdin=PIPE, stdout=PIPE, universal_newlines=True)

DEPTH = 14


@app.route("/getAnalysis", methods=['GET'])
def get_analysis():
    # Get FEN from request parameters
    fen = request.args.get('fen')

    # Send commands to Stockfish
    stockfish.stdin.write(f"position fen {fen}\n")
    # stockfish.stdin.write("go movetime 100\n")
    stockfish.stdin.write(f"go depth {DEPTH}\n")
    stockfish.stdin.flush()

    # Initialize best_score and best_move to None
    best_score = None
    best_move = None

    # Parse Stockfish's output
    while True:
        line = stockfish.stdout.readline().strip()
        if line.startswith('bestmove'):
            best_move = line.split()[1]
            break
        elif line.startswith('info') and ('cp' in line or 'mate' in line):
            match = re.search(r'score cp (-?\d+)', line)
            if match:
                best_score = int(match.group(1))
            else:
                # If there is no score, it is mate
                best_score = 1e6

            depth_match = re.search(r'depth (\d+)', line)
            if depth_match:
                depth = int(depth_match.group(1))
    # Return the score and best move
    return jsonify({'score': best_score, 'best_move': best_move, 'depth': depth, 'win_rate': cp_to_win_rate(best_score)})


@app.route("/evaluatePosition", methods=['POST'])
def evaluate_position():
    # Get FEN from request parameters
    fen = request.json['fen']
    moves = request.json['moves']

    analysis = {}

    for move in moves:

        # Send commands to Stockfish
        stockfish.stdin.write(f"position fen {fen} moves {move}\n")
        # stockfish.stdin.write("go movetime 10\n")
        stockfish.stdin.write(f"go depth {DEPTH}\n")
        stockfish.stdin.flush()

        # Initialize best_score and best_move to None
        best_score = None
        best_move = None

        # Parse Stockfish's output
        while True:
            line = stockfish.stdout.readline().strip()

            if line.startswith('bestmove'):
                break
            elif line.startswith('info') and ('cp' in line or 'mate' in line):
                match = re.search(r'score cp (-?\d+)', line)
                if match:
                    best_score = int(match.group(1))
                else:
                    # It is mate
                    best_score = -1e6

                depth_match = re.search(r'depth (\d+)', line)
                if depth_match:
                    depth = int(depth_match.group(1))

        analysis[move] = {'score': best_score*-1, 'depth': depth,
                          'win_rate': cp_to_win_rate(best_score*-1)}
        # Return the score and best move
    return jsonify({'analysis': analysis})


@app.route("/getEval", methods=['GET'])
def get_eval():
    # Get FEN from request parameters
    fen = request.args.get('fen')

    # Send commands to Stockfish
    stockfish.stdin.write(f"position fen {fen}\n")
    stockfish.stdin.write("eval\n")
    stockfish.stdin.flush()

    # Initialize evaluation data
    classical_eval = {}
    final_eval = None

    # Initial piece mapping
    piece_values = {}

    while True:
        line = stockfish.stdout.readline().strip()

        if "Term" in line:
            next(stockfish.stdout)
            next(stockfish.stdout)
            for x in range(13):
                line = next(stockfish.stdout)
                # Remove | and spaces from the line
                line = line.replace('|', '').split()
                line = [None if i == '----' else i for i in line]
                if x == 8:
                    line[0] = 'King safety'
                    del line[1]
                classical_eval[line[0]] = {
                    'White MG': line[1], 'White EG': line[2], 'Black MG': line[3], 'Black EG': line[4], 'Total MG': line[5], 'Total EG': line[6]
                }

            next(stockfish.stdout)
            line = next(stockfish.stdout)
            line = line.replace('|', '').split()
            line = [None if i == '----' else i for i in line]
            classical_eval['Total'] = {
                'White MG': line[1], 'White EG': line[2], 'Black MG': line[3], 'Black EG': line[4], 'Total MG': line[5], 'Total EG': line[6]
            }

        # Start parsing when NNUE derived piece values begin
        if 'NNUE derived piece values:' in line:
            next(stockfish.stdout)
            # Each piece value output is 8 lines long (1 header, 8 chessboard ranks)
            for rank in range(8):

                # Read and process the two lines representing a rank of the chessboard
                pieces_line = stockfish.stdout.readline().strip().split('|')[
                    1:-1]
                values_line = stockfish.stdout.readline().strip().split('|')[
                    1:-1]
                next(stockfish.stdout)

                # Iterate over each file (column) of the chessboard
                for file in range(8):
                    # Offset by 1 to skip border
                    piece = pieces_line[file].strip()
                    value = values_line[file].strip()

                    if piece and value:
                        # The piece name is case insensitive for matching

                        # Convert the value to a float and store it
                        value = float(value)
                        square = chr(97 + file) + str(8 - rank)
                        piece_values[square] = {"piece": piece, "value": value}

            # Skip the footer line of the table
            next(stockfish.stdout)

        # Get final evaluation
        if 'Final evaluation' in line:
            values = line.split(' ')
            # Removes empty strings from the list
            values = list(filter(None, values))
            final_eval = values[2]
            break

    # Return the evaluation details
    return jsonify({'classical_eval': classical_eval,
                    'nnue_piece_values': piece_values,
                    'final_eval': final_eval})


def cp_to_win_rate(cp):
    return 1 / (1 + math.pow(10, -cp / 400))


@register
def cleanup(): stockfish.kill()


if __name__ == "__main__":
    app.run(port=8002)
