// import type { PageLoad } from './$types';
import type { Actions } from './$types.js';

// Data flow highly inspired by https://joyofcode.xyz/sveltekit-data-flow
export const load = async ({ parent }) => {
	// `parent` is the return value of `+layout.server.ts`
    const parentData = await parent();
    const parentDataWithoutBackEndConfiguration = Object.fromEntries(
        Object.entries(parentData).filter(([key]) => !key.startsWith('backendAPIConfiguration'))
    );
	console.log('=== playground - dataflow - +page.server.ts ===');
	console.log(parentDataWithoutBackEndConfiguration); // { layoutServerTs: 1 }
	// return new data
	return {
		...parentData,
		pageServerTs: 3
	};
};

export const actions: Actions = {
    // When using named actions, the default action cannot be used.
    // default: async ( event ) => { 
    //     // can also be `async ({ request }) => ...
    //     const data = await event.request.formData();
    //     console.log('=== playground - dataflow - +page.server.ts - defaultAction ===');
    //     console.log(data); // FormData object with the submitted form data
    //     // You can process the form data here and return a response
    //     console.log(event)
    //     return {
    //         message: 'Return from default action.',
    //         input: data.get('inputDefault')
    //     };
    // },

    named: async ( event ) => {
        // can also be `async ({ request }) => ...
        const data = await event.request.formData();
        console.log('=== playground - dataflow - +page.server.ts - namedAction===');
        console.log(data); // FormData object with the submitted form data
        // You can process the form data here and return a response
        // console.log(event)
        return {
            message: 'Return from named action.',
            input: data.get('inputNamed')
        };
    },

    enhanced: async ( event ) => {
        // can also be `async ({ request }) => ...
        const data = await event.request.formData();
        console.log('=== playground - dataflow - +page.server.ts - enhancedAction ===');
        console.log(data); // FormData object with the submitted form data
        // You can process the form data here and return a response
        console.log(event)
        return {
            message: 'Return from enhanced action.',
            input: data.get('inputEnhanced')
        };
    },
}