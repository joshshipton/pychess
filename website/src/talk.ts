import { Model, createModel } from 'vosk-browser/dist/vosk.js';

const resultsContainer = document.getElementById('results')!;
const partialContainer = document.getElementById('partial')!;
const sampleRate = 48000;
let channel: MessageChannel = new MessageChannel();
let model: Model | null = null;
let isTranscribing = false;
let mediaStream: MediaStream | null = null;
let recogniser_id : string | null = null;

const load_model = async () => {
    // Request permission to use microphone
    await navigator.mediaDevices.getUserMedia({
        video: false,
        audio: {
            echoCancellation: true,
            noiseSuppression: true,
            channelCount: 1,
            sampleRate
        },
    });

    channel = new MessageChannel();
    model = await createModel('http://127.0.0.1:8080/vosk-model-small-en-us-0.15.tar.gz')
    model.registerPort(channel.port1);

    const recogniser = new model.KaldiRecognizer(sampleRate);
    recogniser_id = recogniser.id;
    recogniser.setWords(true);
    recogniser.on("result", (message: any) => {
        const result = message.result;
        console.log(JSON.stringify(result, null, 2));

        // Adds to the results container
        const p = document.createElement('span');
        p.innerText = `${result.text} `;
        resultsContainer.insertBefore(p, partialContainer);
    });
    recogniser.on("partialresult", (message: any) => {
        const partial = message.result.partial;
        partialContainer.textContent = partial;
    });
}

load_model();

window.addEventListener('keydown', event => {
    if (event.key === 'v' && !isTranscribing) {
        console.log('Starting transcription');
        isTranscribing = true;
        startTranscription();
    }
});

window.addEventListener('keyup', event => {
    if (event.key === 'v' && isTranscribing) {
        console.log('Stopping transcription');
        isTranscribing = false;
        stopTranscription();
    }
});

const startTranscription = async () => {
    // Start audio capture
    mediaStream = await navigator.mediaDevices.getUserMedia({
        video: false,
        audio: {
            echoCancellation: true,
            noiseSuppression: true,
            channelCount: 1,
            sampleRate
        },
    });

    console.log('Starting transcription');

    const audioContext = new AudioContext();
    await audioContext.audioWorklet.addModule('recognizer-processor.js')
    const recognizerProcessor = new AudioWorkletNode(audioContext, 'recognizer-processor', { channelCount: 1, numberOfInputs: 1, numberOfOutputs: 1 });
    recognizerProcessor.port.postMessage({ action: 'init', recognizerId: recogniser_id }, [channel.port2])
    recognizerProcessor.connect(audioContext.destination);

    const source = audioContext.createMediaStreamSource(mediaStream);
    source.connect(recognizerProcessor);
}

const stopTranscription = () => {
    if (mediaStream) {
        const tracks = mediaStream.getTracks();
        tracks.forEach((track) => {
            track.stop();
        });
    }

}