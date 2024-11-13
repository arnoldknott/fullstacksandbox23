import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';
import { svelteTesting } from '@testing-library/svelte/vite';

export default defineConfig({
	plugins: [sveltekit(), svelteTesting()],
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
	},
});
