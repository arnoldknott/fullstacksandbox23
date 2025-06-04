import type { Actions } from './$types';
import { fail } from '@sveltejs/kit';

export const actions: Actions = {
    share: async ({ request, url }) => {
        const data = await request.formData();
        // const sessionId = locals.sessionData.sessionId;

        const identityId= url.searchParams.get('identity-id')?.toString();
        const newAction = url.searchParams.get('new-action')?.toString()

        // Call the backendAPI.share() here to perform the necessary action
        console.log('=== routes - playground - share action executed - following data ready to be sent to backend ===');
        console.log(
            "Resource Id: ", data.get('id')?.toString(), "\n",
            "Identity Id: ", identityId, "\n",
            "Action: ", url.searchParams.get('action')?.toString(), "\n",
            "NewAction: ", newAction
        );

        const confirmedNewAction = newAction === "unshare" ? "" :  newAction
        // return fail(500, {
        //     error: 'This action is not implemented yet. Please check the console for more details.'
        // });
        return {
            identityId: identityId,
            confirmedNewAction: confirmedNewAction,
        }
    }
};