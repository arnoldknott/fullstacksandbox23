// import type { PageLoad } from './$types';
import type { Actions } from './$types.js';
import { error, fail, redirect } from '@sveltejs/kit';

// Data flow highly inspired by https://joyofcode.xyz/sveltekit-data-flow
export const load = async ({ parent }) => {
	// `parent` is the return value of `+layout.server.ts`
	const parentData = await parent();
	const cleanedParentData = Object.fromEntries(
		Object.entries(parentData).filter(([key]) => !key.startsWith('backendAPIConfiguration') && !key.startsWith('session'))
	);
	console.log('=== playground - dataflow - +page.server.ts ===');
	console.log(cleanedParentData); // { layoutServerTs: 1 }
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

	named: async (event) => {
		// can also be `async ({ request, ... }) => ...
		// This is a good place to validate the form data before sending it to the database, backend, or elsewhere.
		const data = await event.request.formData();
		console.log('=== playground - dataflow - +page.server.ts - namedAction===');
		console.log(data); // FormData object with the submitted form data
		// console.log(event)
		return {
			message: 'Return from named action.',
			input: data.get('inputNamed')
		};
	},

	enhanced: async (event) => {
		// can also be `async ({ request }) => ...
		const data = await event.request.formData();
		console.log('=== playground - dataflow - +page.server.ts - enhancedAction ===');
		console.log(data); // FormData object with the submitted form data
		// console.log(event)
		return {
			message: 'Return from enhanced action.',
			input: data.get('inputEnhanced')
		};
	},

	submitFunction: async (event) => {
		// can also be `async ({ request }) => ...
		const data = await event.request.formData();
		console.log('=== playground - dataflow - +page.server.ts - submitFunction ===');
		console.log(data); // FormData object with the submitted form data
		// console.log(event)
		return {
			message: 'Return from submitFunction action.',
			input: data.get('inputSubmit')
		};
	},

	submitFunctionWithCallback: async (event) => {
		// can also be `async ({ request }) => ...
		const data = await event.request.formData();
		console.log('=== playground - dataflow - +page.server.ts - submitFunctionWithCallback ===');
		console.log(data); // FormData object with the submitted form data
		console.log(event);
		return {
			message: 'Return from submitFunction with Callback action.',
			input: data.get('inputSubmitWithCallback')
		};
	},

	submitFunctionWithCallBackAndApplyAction: async (event) => {
		// can also be `async ({ request }) => ...
		const data = await event.request.formData();
		console.log(
			'=== playground - dataflow - +page.server.ts - submitFunctionWithCallbackAndApplyAction ==='
		);
		console.log(data); // FormData object with the submitted form data
		// console.log(event)
		return {
			message: 'Return from submitFunction with Callback and applyAction() action.',
			input: data.get('inputSubmitWithCallBackAndApplyAction')
		};
	},

	submitFunctionWithCallBackAndUpdate: async (event) => {
		// can also be `async ({ request }) => ...
		const data = await event.request.formData();
		console.log(
			'=== playground - dataflow - +page.server.ts - submitFunctionWithCallbackAndUpdate ==='
		);
		console.log(data); // FormData object with the submitted form data
		console.log(event);

		return {
			message: 'Return from submitFunction with Callback and update() action.',
			input: data.get('inputSubmitFunctionWithCallBackAndUpdate')
		};
	},

	redirectServerSide: async (event) => {
		// can also be `async ({ request }) => ...
		const data = await event.request.formData();
		console.log('=== playground - dataflow - +page.server.ts - redirectServerSide ===');
		console.log(data); // FormData object with the submitted form data
		// console.log(event)
		redirect(303, 'dataflow/redirect');
	},

	// Can be used for data validation, f.x. to check if the input is valid before sending it to the backend.
	expectedErrorCausesFail: async (event) => {
		// can also be `async ({ request }) => ...
		const data = await event.request.formData();
		console.log('=== playground - dataflow - +page.server.ts - expectedErrorCausesFail ===');
		console.log(data); // FormData object with the submitted form data
		// console.log(event)
		return fail(409, {
			error: 'Expected error causes fail action.',
			input: data.get('inputExpectedErrorCausesFail')
		});
	},

	unexpectedErrorInBackend: async (event) => {
		// can also be `async ({ request }) => ...
		const data = await event.request.formData();
		console.log('=== playground - dataflow - +page.server.ts - unexpectedErrorInBackend ===');
		console.log(data); // FormData object with the submitted form data
		// console.log(event)
		try {
			// Simulating an unexpected error in the backend action, f.x. a 500 error from database or API
			throw new Error('Unexpected error in backend action: unexpectedErrorInBackend');
		} catch (err) {
			console.error(err);
			// This also causes an error in the console on client side:
			error(400, err instanceof Error ? err : String(err));
		}
	}
};
