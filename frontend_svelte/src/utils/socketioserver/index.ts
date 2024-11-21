import type { Server } from "socket.io";

export const socketIoEvents = (io: Server) => {
    io.on('connection', (socket) => {
        socket.emit('eventFromServer', 'Hello, World 👋')
    })
}