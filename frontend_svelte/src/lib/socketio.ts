import { getContext } from "svelte";

export class SocketIO {
    // private socket: WebSocket;


    constructor() {
        console.log('=== class socket IO instantiated ===');
        const clientConfiguration = getContext('clientConfiguration');
        console.log("=== lib - socketio.ts - clientConfiguration ===");
        console.log('clientConfiguration:', clientConfiguration);
    }

    // constructor() {
    //     this.socket = new WebSocket('ws://localhost:8660');
    //     this.socket.onopen = () => {
    //         console.log('=== socket opened ===');
    //     };
    //     this.socket.onmessage = (event) => {
    //         console.log('Message from server:', event.data);
    //     };
    // }

    // sendMessage(message: string) {
    //     this.socket.send(message);
    // }
    sendMessage(message: string) {
        console.log('Message sent:', message);
    }
}

// import { io } from 'socket.io-client';

// let socketio_client: any;
// let new_message: string = '';
// let old_messages: string[] = [];

// socketio_client = io('http://localhost:8660');
// socketio_client.on('connect', () => {
//     console.log('=== socket opened ===');
//     socketio_client.send('Hello from the client!');
// });

// socketio_client.on('demo_message', (data: string) => {
//     console.log('Message from server:', data);
//     old_messages.push(data);
// });
// });

// const sendMessage = (event: Event) => {
// event.preventDefault();
// socketio_client.emit('demo_message', new_message);