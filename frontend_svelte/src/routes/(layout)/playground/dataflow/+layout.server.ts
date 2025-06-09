import type { PageLoad } from './$types';

// Data flow highly inspired by https://joyofcode.xyz/sveltekit-data-flow
export const load: PageLoad = async () => {
	console.log('=== playground - dataflow - +layout.server.ts ===');
	return {
		layoutServerTs: 1
	};
};
