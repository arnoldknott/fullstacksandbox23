import { createRequire } from 'node:module';

import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { svelteTesting } from '@testing-library/svelte/vite';
import { defineConfig } from 'vitest/config';
const require = createRequire(import.meta.url);

export default defineConfig({
	plugins: [sveltekit(), svelteTesting(), tailwindcss()],
	server: {
		host: '0.0.0.0',
		hmr: {
			clientPort: 8661
		},
		port: 80 // prod is still on 3000, which is the default port in /app/index.js (look at the end). TBD (less urgent): review build process.
	},
	// css: {
	// 	postcss: './postcss.config.js'
	// },
	test: {
		environment: 'jsdom',
		setupFiles: ['./vitest-setup.js'],
		include: ['src/**/*.{test,spec}.{js,ts}'],
		    alias: {
        // Override svelteTesting()'s `browser` condition for `ws` only.
        // The Svelte browser runtime stays intact; only the Node server's
        // WebSocket engine is forced to the real implementation.
        ws: require.resolve('ws')
    }
	}
});
