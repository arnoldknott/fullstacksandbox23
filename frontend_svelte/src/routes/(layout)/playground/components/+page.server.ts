import type { Actions } from './$types';
// import { fail } from '@sveltejs/kit';

export const actions: Actions = {
	share: async ({ request, url }) => {
		const data = await request.formData();
		// const sessionId = locals.sessionData.sessionId;

		const identityId = url.searchParams.get('identity-ids')?.toString();
		const action = url.searchParams.get('action')?.toString();
		const newAction = url.searchParams.get('new-action')?.toString();

		// Call the backendAPI.share() here to perform the necessary action
		console.log(
			'=== playground - server - share action executed - following data ready to be sent to backend ==='
		);
		console.log(
			'Resource Id: ' + data.get('id')?.toString() + '\n',
			'Identity Id: ' + identityId + '\n',
			'Action: ' + action + '\n',
			'NewAction: ' + newAction
		);

		let confirmedNewAction = undefined;
		if (action) {
			if (!newAction || newAction === 'undefined') {
				console.log('=== assigning action to confirmedNewAction ===');
				confirmedNewAction = action;
			} else {
				console.log('=== assigning newAction to confirmedNewAction ===');
				confirmedNewAction = newAction;
			}
		}
		// return fail(500, {
		//     error: 'This action is not implemented yet. Please check the console for more details.'
		// });

		const returnObject: { identityId: string | undefined; confirmedNewAction?: string } = {
			identityId: identityId
		};
		if (confirmedNewAction) {
			returnObject.confirmedNewAction = confirmedNewAction;
		}
		console.log('=== playground - server - share action executed - returning following object ===');
		console.log(returnObject);
		return returnObject;
	}
};
