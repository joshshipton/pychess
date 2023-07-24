import { Chessground } from 'chessground';
import {
    init,
    classModule,
    propsModule,
    styleModule,
    eventListenersModule,
    h,
} from 'snabbdom';
const patch = init([
    classModule, // makes it easy to toggle classes
    propsModule, // for setting properties on DOM elements
    styleModule, // handles styling on elements with support for animations
    eventListenersModule, // attaches event listeners
]);

const config = {};
const ground = Chessground(document.getElementById('chessground')!, config);

// Using snabbdom
// Button to get fen
const getFenButton = document.getElementById('get-fen')!;
getFenButton.addEventListener('click', () => {
    const fen = ground.getFen();
});

// Button to get drawn arrows
const getArrowsButton = document.getElementById('get-arrows')!;
getArrowsButton.addEventListener('click', () => {
    const fen = ground.getFen();
    const state = ground.state;
    const shapes = state.drawable.shapes;
});