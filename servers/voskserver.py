# flask --app voskserver.py --debug run -p 8080
from flask import Flask, send_from_directory

app = Flask(__name__, static_url_path='')

@app.route('/models/<path:path>')
def serve_model(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)