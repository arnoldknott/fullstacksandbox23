import { fail, redirect } from '@sveltejs/kit';

import { IdentityProvider } from '$lib/identityProvider';
import { backendAPI } from '$lib/server/apis/backendApi';
import { redisCache } from '$lib/server/cache';
import { type AccountMergeState, providerProofToken } from '$lib/server/oauth/accountLink';

import type { Actions, PageServerLoad } from './$types';

async function mergeState(sessionId: string): Promise<AccountMergeState> {
	const state = await redisCache.getSession<AccountMergeState>(sessionId, '$.accountMerge');
	if (!state || state.expiresAt <= Date.now()) {
		if (state) await clearMergeState(sessionId, state.linkedProvider);
		redirect(303, '/');
	}
	return state;
}

async function clearMergeState(sessionId: string, linkedProvider: IdentityProvider): Promise<void> {
	await redisCache.deleteSessionPath(sessionId, '$.accountMerge');
	await redisCache.deleteSessionPath(
		sessionId,
		linkedProvider === IdentityProvider.MICROSOFT ? '$.microsoftAccount' : '$.linkedinSubject'
	);
}

export const load: PageServerLoad = async ({ locals, url }) => {
	const debug = url.searchParams.get('debug') === 'true';
	if (debug) {
		const merge: AccountMergeState = {
			result: 'merge-required',
			preview_hash: 'example_preview_hash',
			settings: {
				ai_enabled: { survivor: true, source: false },
				theme_color: { survivor: '#0e33ef', source: '#e2f10f' },
				theme_variant: { survivor: 'Variant', source: 'TonalSpot' },
				contrast: { survivor: 0.2, source: -0.4 }
			},
			defaults: {
				ai_enabled: 'survivor',
				theme_color: 'survivor',
				theme_variant: 'source',
				contrast: 'source'
			},
			linkedProvider: IdentityProvider.LINKEDIN,
			targetUrl: '/',
			expiresAt: Date.now() + 600000
		};
		return { merge };
	}
	return {
		merge: await mergeState(locals.sessionData.sessionId)
	};
};

export const actions: Actions = {
	confirm: async ({ request, locals, cookies }) => {
		const sessionId = locals.sessionData.sessionId;
		const state = await mergeState(sessionId);
		const form = await request.formData();
		const choices = Object.fromEntries(
			Object.keys(state.settings).flatMap((key) => {
				const value = form.get(key);
				return value === 'source' || value === 'survivor' ? [[key, value]] : [];
			})
		);
		const linkedToken = await providerProofToken(sessionId, state.linkedProvider);
		const response = await backendAPI.post(
			sessionId,
			'/user/me/link/confirm',
			JSON.stringify({ preview_hash: state.preview_hash, choices }),
			undefined,
			{},
			{ 'X-Account-Link-Authorization': `Bearer ${linkedToken}` }
		);
		if (!response.ok) return fail(response.status, { error: await response.text() });
		const provider = locals.sessionData.identityProvider ?? IdentityProvider.MICROSOFT;
		cookies.delete('session_id', { path: '/' });
		redirect(303, `/login/${provider}?target-url=${encodeURIComponent(state.targetUrl || '/')}`);
	},
	abandon: async ({ locals }) => {
		const state = await mergeState(locals.sessionData.sessionId);
		await clearMergeState(locals.sessionData.sessionId, state.linkedProvider);
		redirect(303, state.targetUrl || '/');
	}
};
