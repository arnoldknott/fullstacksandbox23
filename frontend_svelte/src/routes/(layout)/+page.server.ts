import type { Actions } from './$types';
import { Variant } from '$lib/theming';
import { backendAPI } from '$lib/server/apis';
import { fail } from '@sveltejs/kit';

export const actions: Actions = {
	default: async ({ locals, request }) => {
		const data = await request.formData();
		const sessionId = locals.sessionData.sessionId;
		console.log('=== layout - layout.server - putProfile - sessionData.userProfile.id ===');
		console.log(locals.sessionData.userProfile?.id);
		console.log('=== layout - layout.server - putProfile - data ===');
		console.log(data);
		if (locals.sessionData.userProfile?.id) {
			const variant = data.get('variant-picker');
			console.log('=== layout - layout.server - putProfile - variant ===');
			console.log(variant);
			const contrast = parseFloat(data.get('contrast') as string);

			const payload = {
				id: locals.sessionData.userProfile.id,
				user_profile: {
					theme_color: data.get('color-picker'),
					theme_variant: variant,
					// theme_variant: "Neutral",
					contrast: contrast
				}
			};
			const response = await backendAPI.put(sessionId, '/user/me', JSON.stringify(payload));
			if (response.status !== 200) {
				return fail(response.status, { error: response.statusText });
			}
            // console.log('=== layout - layout.server - putProfile - locals.sessionData.userProfile ===');
            // console.log(locals.sessionData.userProfile);
		}
	}
};
