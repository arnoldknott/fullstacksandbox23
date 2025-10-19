import type { Actions } from './$types';
import { backendAPI } from '$lib/server/apis/backendApi';
import { fail } from '@sveltejs/kit';
import { redisCache } from '$lib/server/cache';
import { Variant } from '$lib/theming';

export const actions: Actions = {
	putme: async ({ locals, request }) => {
		const data = await request.formData();
		const sessionId = locals.sessionData.sessionId;
		// console.log('=== layout - layout.server - putProfile - sessionData.currentUser.id ===');
		// console.log(locals.sessionData.currentUser?.id);
		// console.log('=== layout - layout.server - putProfile - data ===');
		// console.log(data);
		if (locals.sessionData.currentUser?.id) {
			const color = data.get('color-picker');
			const variant = data.get('variant-picker');
			const contrast = parseFloat(data.get('contrast') as string);

			// TBD: consider moving this to layout.server.ts?
			const payload = {
				id: locals.sessionData.currentUser.id,
				user_profile: {
					theme_color: color,
					theme_variant: variant,
					// theme_variant: "Neutral",
					contrast: contrast
				}
			};
			// console.log('=== layout - layout.server - putProfile - payload - user_profile ===');
			// console.log(payload.user_profile);
			const response = await backendAPI.put(sessionId, '/user/me', JSON.stringify(payload));
			if (response.status !== 200) {
				return fail(response.status, { error: response.statusText });
			}
			// console.log('=== layout - layout.server - putProfile - locals.sessionData.currentUser ===');
			// console.log(locals.sessionData.currentUser);
			await redisCache.setSession(
				sessionId,
				'$.currentUser.user_profile.theme_color',
				JSON.stringify(payload.user_profile.theme_color)
			);
			await redisCache.setSession(
				sessionId,
				'$.currentUser.user_profile.theme_variant',
				JSON.stringify(payload.user_profile.theme_variant)
			);
			await redisCache.setSession(
				sessionId,
				'$.currentUser.user_profile.contrast',
				JSON.stringify(payload.user_profile.contrast)
			);
			if (payload.user_profile.theme_color) {
				locals.sessionData.currentUser.user_profile.theme_color = color as string;
			}
			if (payload.user_profile.theme_variant) {
				locals.sessionData.currentUser.user_profile.theme_variant = variant as Variant;
			}
			if (payload.user_profile.contrast) {
				locals.sessionData.currentUser.user_profile.contrast = Number(contrast);
			}
			// console.log('=== layout - layout.server - putProfile - locals.sessionData.currentUser ===');
			// console.log(locals.sessionData.currentUser);
		}
	}
};
