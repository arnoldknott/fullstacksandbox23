import { defineConfig } from 'vitest/config';
import type { ViteDevServer } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { svelteTesting } from '@testing-library/svelte/vite';
import { Server } from "socket.io";
import { socketIoEvents } from './src/utils/socketioserver/index.ts';


const socketIOServer = {
	name: 'SocketIOServer',
	configureServer(server: ViteDevServer) {
		if (!server.httpServer) return

		const io = new Server(server.httpServer);// options as 2nd argument: { cors: {origin: "https://example.com"} }
		console.log('👍💉 vite.config.ts - socketIOServer - SocketIO injected');
		socketIoEvents(io);
	}
}


export default defineConfig({
	plugins: [sveltekit(), svelteTesting(), socketIOServer],
	server: {
		host: '0.0.0.0',
		hmr: {
			clientPort: 8661
		},
		port: 80 // prod is still on 3000, which is the default port in /app/index.js (look at the end). TBD (less urgent): review build process.
	},
	test: {
		environment: 'jsdom',
		setupFiles: ['./vitest-setup.js'],
		include: ['src/**/*.{test,spec}.{js,ts}']
	}
});
