import type { LayoutServerLoad, LayoutData } from './$types';

// Data flow highly inspired by https://joyofcode.xyz/sveltekit-data-flow
export const load: LayoutServerLoad = async ({ data }: LayoutData) => {
	// `data` is the return value of `+layout.server.ts`
	console.log('=== playground - dataflow - +layout.ts ===');
	const cleanedData = Object.fromEntries(
		Object.entries(data).filter(
			([key]) =>
				key.startsWith('layoutServerTs') ||
				key.startsWith('layoutTs') ||
				key.startsWith('pageServerTs') ||
				key.startsWith('pageTs')
		)
	);
	console.log(cleanedData); // { layoutServerTs: 1 }
	// return new data
	return {
		...data,
		layoutTs: 2
	};
};
