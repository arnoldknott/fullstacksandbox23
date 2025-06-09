// import type { PageLoad } from './$types';

// Data flow highly inspired by https://joyofcode.xyz/sveltekit-data-flow
export const load = async ( {parent} ) => {
    // `parent` is the return value of `+layout.server.ts`
    const data = await parent();
    console.log('=== playground - dataflow - +layout.ts ===');
    console.log(data) // { layoutServerTs: 1, layoutTs: 2, pageServerTs: 3 }
    // return new data
    return {
        ...data,
        pageServerTs: 3
    }
}