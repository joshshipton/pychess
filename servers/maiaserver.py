# flask --app maiaserver.py --debug run -p 8001

import re
from flask import Flask, request, jsonify
from subprocess import Popen, PIPE
from atexit import register

app = Flask(__name__)
lc0_1900 = Popen(
    ['lc0', '--weights=maia-1900.pb', '-v'], stdin=PIPE, stdout=PIPE, universal_newlines=True)
lc0_1100 = Popen(
    ['lc0', '--weights=maia-1100.pb', '-v'], stdin=PIPE, stdout=PIPE, universal_newlines=True)


@app.route("/getMove", methods=['GET'])
def get_move():
    lc0_1900.stdin.write(
        f"position fen {request.args.get('fen')}\ngo nodes 1\n")
    lc0_1900.stdin.flush()

    move_distribution_1900 = {}
    bestmove_1900 = None
    for line in lc0_1900.stdout:
        if re.match(r'^info string', line) and not re.match(r'^info string node', line):
            move = re.search(r'\b\w+\b', line.split("string")[1]).group()
            match = re.search(r'\(P:[^)]+\)', line)
            if match:
                probability = round(float(match.group()[3:-2].strip())/100, 4)
                # four decimal places
                move_distribution_1900[move] = probability
        elif re.match(r'^bestmove', line):
            bestmove_1900 = re.search(
                r'\b\w+\b', line.split("bestmove")[1]).group()
            break

    lc0_1100.stdin.write(
        f"position fen {request.args.get('fen')}\ngo nodes 1\n")
    lc0_1100.stdin.flush()

    move_distribution_1100 = {}
    bestmove_1100 = None
    for line in lc0_1100.stdout:
        if re.match(r'^info string', line) and not re.match(r'^info string node', line):
            move = re.search(r'\b\w+\b', line.split("string")[1]).group()
            match = re.search(r'\(P:[^)]+\)', line)
            if match:
                probability = round(float(match.group()[3:-2].strip())/100, 4)
                # four decimal places
                move_distribution_1100[move] = probability
        elif re.match(r'^bestmove', line):
            bestmove_1100 = re.search(
                r'\b\w+\b', line.split("bestmove")[1]).group()
            break

    return jsonify({
        "maia-1900": {"moves": move_distribution_1900, "bestmove": bestmove_1900},
        "maia-1100": {"moves": move_distribution_1100, "bestmove": bestmove_1100}
    })


@register
def cleanup(): lc0_1900


if __name__ == "__main__":
    PORT = 8001
    print(f"Running on port {PORT}")
    app.run(port=PORT)
