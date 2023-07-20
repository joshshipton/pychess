# flask --app blunderserver.py --debug run -p 8003

import torch
from flask import Flask, request, jsonify
from subprocess import Popen, PIPE
from atexit import register
from haibrid_chess_utils import fen_to_vec

# Load the model
model = torch.load('leela_blunder_00001-266000.pt', map_location=torch.device('cpu'))
model.eval()  # Set the model to evaluation mode


app = Flask(__name__)

@app.route("/getBlunder", methods=['GET'])
def get_move():
    fen = request.args.get('fen')
    vec = fen_to_vec.fenToVec(fen)

    # Convert the vector to a PyTorch tensor and add an extra dimension
    vec = torch.tensor(vec).unsqueeze(0).float()

    # Make a prediction
    with torch.no_grad():  # No need to calculate gradients for this step
        prediction = model(vec)

    print(prediction)
    return jsonify({"blunder_chance": prediction[0][0].item()})

if __name__ == "__main__":
    PORT = 8003
    print(f"Running on port {PORT}")
    app.run(port=PORT)