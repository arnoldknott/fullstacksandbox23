import type { Actions } from './$types';
import { backendAPI } from '$lib/server/apis';
import { fail } from '@sveltejs/kit';
import { redisCache } from '$lib/server/cache';

export const actions: Actions = {
	putme: async ({ locals, request }) => {
		const data = await request.formData();
		const sessionId = locals.sessionData.sessionId;
		// console.log('=== layout - layout.server - putProfile - sessionData.userProfile.id ===');
		// console.log(locals.sessionData.userProfile?.id);
		// console.log('=== layout - layout.server - putProfile - data ===');
		// console.log(data);
		if (locals.sessionData.userProfile?.id) {
			const variant = data.get('variant-picker');
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
			await redisCache.setSession(
				sessionId,
				'$.userProfile.user_profile.theme_color',
				JSON.stringify(payload.user_profile.theme_color)
			);
			await redisCache.setSession(
				sessionId,
				'$.userProfile.user_profile.theme_variant',
				JSON.stringify(payload.user_profile.theme_variant)
			);
			await redisCache.setSession(
				sessionId,
				'$.userProfile.user_profile.contrast',
				JSON.stringify(payload.user_profile.contrast)
			);
			// locals.sessionData.userProfile.user_profile.theme_color = payload.user_profile.theme_color;
			// locals.sessionData.userProfile.user_profile.theme_variant =
			// 	payload.user_profile.theme_variant;
			// locals.sessionData.userProfile.user_profile.contrast = payload.user_profile.contrast;
			// console.log('=== layout - layout.server - putProfile - locals.sessionData.userProfile ===');
			// console.log(locals.sessionData.userProfile);
		}
	}
};
