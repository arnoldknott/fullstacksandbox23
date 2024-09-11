import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: '0.0.0.0',
		hmr: {
			clientPort: 8661
		},
		port: 80 // prod is still on 3000, which is the default port in /app/index.js (look at the end). TBD (less urgent): review build process.
	},
	test: {
		environment: 'jsdom',
		include: ['src/**/*.{test,spec}.{js,ts}']
	}
});
