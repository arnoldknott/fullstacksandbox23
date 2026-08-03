import { createRequire } from 'node:module';

import { svelteTesting } from '@testing-library/svelte/vite';
import { defineConfig, mergeConfig } from 'vitest/config';

import viteConfig from './vite.config.ts';

const require = createRequire(import.meta.url);

export default mergeConfig(
	viteConfig,
	defineConfig({
		plugins: [svelteTesting()],
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
	})
);
