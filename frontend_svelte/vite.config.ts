import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: '0.0.0.0',
		hmr: {
			clientPort: 8661
		},
		port: 80
	},
  // define: {
  //   'process.env.BACKEND_HOST': JSON.stringify(process.env.BACKEND_HOST),
	// 	'process.env.BACKEND_PORT': JSON.stringify(process.env.BACKEND_PORT),
  // },
	test: {
		environment: 'jsdom',
		include: ['src/**/*.{test,spec}.{js,ts}']
	}
});
