import './chess-thing.ts'

import {
    init,
    classModule,
    propsModule,
    styleModule,
    eventListenersModule,
    h,
} from 'snabbdom';


// Initialize snabbdom
const patch = init([
    // Init patch function with chosen modules
    classModule, // makes it easy to toggle classes
    propsModule, // for setting properties on DOM elements
    styleModule, // handles styling on elements with support for animations
    eventListenersModule, // attaches event listeners
]);

// Create a variable to store the MediaRecorder object
let mediaRecorder: MediaRecorder | null = null;
let recording_number = 1;
let recording: Blob | null = null;

// Get user's audio from the microphone

window.onload = () => {
    console.log('window loaded');
    // get audio stream from user's mic
    navigator.mediaDevices.getUserMedia({
        audio: true
    }).then(function (stream) {
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.addEventListener('dataavailable', onRecordingReady);
    }).catch(err => {
        console.log('The following getUserMedia error occurred: ' + err);
    })
}

const start_recording = (e: Event) => {
    console.log('start recording');
    if (!mediaRecorder) {
        console.log('mediaRecorder is null');
        return;
    }
    console.log(mediaRecorder);
    mediaRecorder.start();
}

const stop_recording = (e: Event) => {
    console.log('stop recording');
    if (!mediaRecorder) {
        console.log('mediaRecorder is null');
        return;
    }
    mediaRecorder.stop();
};

const download = (url: string, name: string) => {
    const a = document.createElement('a');

    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
};

const onRecordingReady = (e: BlobEvent) => {
    // Logs the recording to the console
    console.log(e);
    // Creates a new recording
    const name = `recording-${recording_number++}`;
    const url = URL.createObjectURL(e.data);

    // Adds a button to download the recording
    const downloadButton = h('button#download', { on: { click: () => download(url, name) } }, 'Download');
    patch(document.getElementById('download')!, downloadButton);

    // Saves blob to recording
    recording = e.data;
};

const send = (e: Event) => {
    console.log('send');
    // Posts a wav file of blob recording to http://127.0.0.1:8004
    if (!recording) {
        console.log('recording is null');
        return;
    }

    // Saves as an mp3

    console.log('sending');
    let formData = new FormData();
    formData.append('file', recording, 'recording.wav');

    fetch('http://127.0.0.1:8004/transcribe', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            console.log('Upload successful!');
        } else {
            console.error('Upload failed!');
        }
    }).catch(error => console.error('Error:', error));

}

const start_node = h('button#start', { on: { click: start_recording } }, 'Start');
patch(document.getElementById('start')!, start_node);

// changes button to start recording
const stop_node = h('button#stop', { on: { click: stop_recording } }, 'Stop');
patch(document.getElementById('stop')!, stop_node);