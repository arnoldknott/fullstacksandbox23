import type { PageLoad, PageData } from './$types';

// Data flow highly inspired by https://joyofcode.xyz/sveltekit-data-flow
export const load: PageLoad = async ({ data, parent }: PageData) => {
	// `data` is the return value of `+layout.server.ts`
	console.log('=== playground - dataflow - +page.ts ===');
	console.log(data); // { layoutServerTs: 1, layout.ts: 2, pageserverTs: 3  }
	const parentData = await parent();
	console.log(parentData); // { layoutServerTs: 1, layoutTs: 2, pageServerTs: 3 }
	// return new data
	return {
		...data,
		...parentData,
		pageTs: 4
	};
};
