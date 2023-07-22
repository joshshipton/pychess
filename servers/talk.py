# flask --app talk.py --debug run -p 8004
# A server that transcribes audio files using the whisper model
from flask import Flask, request, jsonify
import numpy as np
import whisper
import librosa

app = Flask(__name__)

print("Loading model...")

# load the whisper model
model = whisper.load_model("tiny.en")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    print("Transcribing...")
    print(request.files)
    audio_file = request.files['audio']

    # Assuming the audio file is in wav format
    if audio_file and allowed_file(audio_file.filename):
        audio, sr = librosa.load(audio_file, sr=None)
        audio = np.asarray(audio, dtype=np.float32)

        transcription = model.transcribe(audio_file)
        print(transcription)
        return jsonify({'transcription': transcription})
    else:
        print(f"Invalid file format: {audio_file.filename}")
    return jsonify({'error': 'Invalid file format'})

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'wav'}

if __name__ == '__main__':
    app.run(debug=True)