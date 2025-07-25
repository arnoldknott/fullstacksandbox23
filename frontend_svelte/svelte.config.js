import adapter from '@sveltejs/adapter-node';
// import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
// import { vitePreprocess } from '@sveltejs/kit/vite';
import { sveltePreprocess } from 'svelte-preprocess';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://kit.svelte.dev/docs/integrations#preprocessors
	// for more information about preprocessors
	// preprocess: [vitePreprocess()],
	preprocess: [sveltePreprocess()],
	// preprocess: [sveltePreprocess(), vitePreprocess()],
	kit: {
		// adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
		// If your environment is not supported or you settled on a specific environment, switch out the adapter.
		// See https://kit.svelte.dev/docs/adapters for more information about adapters.
		adapter: adapter(),
		alias: {
			$components: './src/components'
			// $lib: './src/lib'
			// '*': './node_modules/*'
		}
	},
	extensions: ['.svelte', '.svx']
};

export default config;
