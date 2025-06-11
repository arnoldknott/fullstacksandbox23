import type { PageLoad, PageData } from './$types';

// Data flow highly inspired by https://joyofcode.xyz/sveltekit-data-flow
export const load: PageLoad = async ({ data, parent }: PageData) => {
	// `data` is the return value of `+layout.server.ts`
	console.log('=== playground - dataflow - +page.ts ===');
	const cleanedData = Object.fromEntries(
		Object.entries(data).filter(
			([key]) =>
				key.startsWith('layoutServerTs') ||
				key.startsWith('layoutTs') ||
				key.startsWith('pageServerTs') ||
				key.startsWith('pageTs')
		)
	);
	console.log(cleanedData); // { layoutServerTs: 1, pageserverTs: 3  }
	const parentData = await parent();
	const cleanedParentData = Object.fromEntries(
		Object.entries(parentData).filter(
			([key]) =>
				key.startsWith('layoutServerTs') ||
				key.startsWith('layoutTs') ||
				key.startsWith('pageServerTs') ||
				key.startsWith('pageTs')
		)
	);
	console.log(cleanedParentData); // { layoutServerTs: 1, layoutTs: 2 }
	// return new data
	return {
		...data,
		...parentData,
		pageTs: 4
	};
};
