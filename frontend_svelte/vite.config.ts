import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit(), tailwindcss()],
	server: {
		host: '0.0.0.0',
		watch: {
			// Docker bind mounts can miss rename events; polling keeps route/type generation in sync.
			usePolling: true,
			interval: 150,
			binaryInterval: 300
		},
		hmr: {
			clientPort: 8661
		},
		port: 80 // prod is still on 3000, which is the default port in /app/index.js (look at the end). TBD (less urgent): review build process.
	}
	// css: {
	// 	postcss: './postcss.config.js'
	// }
});
