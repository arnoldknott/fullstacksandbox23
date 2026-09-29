import { beforeEach, describe, expect, it, vi } from 'vitest';

import { IdentityProvider } from '$lib/identityProvider';
import { backendAPI } from '$lib/server/apis/backendApi';
import { redisCache } from '$lib/server/cache';

import { actions } from './+page.server';
import type { Actions } from './$types';

function event(provider: IdentityProvider) {
	const formData = new FormData();
	formData.set('provider', provider);
	return {
		locals: {
			sessionData: {
				sessionId: 'test-session',
				loggedIn: true,
				sessionOwnerProvider: IdentityProvider.LINKEDIN,
				currentUser: {
					id: 'internal-user',
					azure_user_id: 'microsoft-user',
					linkedin_user_id: 'linkedin-user'
				}
			}
		},
		request: { formData: async () => formData }
	} as Parameters<NonNullable<Actions['unlinkaccount']>>[0];
}

describe('unlinkaccount', () => {
	beforeEach(() => vi.restoreAllMocks());

	it('removes the inactive provider and refreshes the cached user', async () => {
		const updatedUser = {
			id: 'internal-user',
			azure_user_id: 'microsoft-user',
			linkedin_user_id: null
		};
		const remove = vi
			.spyOn(backendAPI, 'delete')
			.mockResolvedValue(new Response(null, { status: 204 }));
		vi.spyOn(backendAPI, 'get').mockResolvedValue(
			new Response(JSON.stringify(updatedUser), { status: 200 })
		);
		const setSession = vi.spyOn(redisCache, 'setSession').mockResolvedValue(true);
		const request = event(IdentityProvider.LINKEDIN);

		await expect(actions.unlinkaccount?.(request)).resolves.toEqual({
			unlinkedProvider: IdentityProvider.LINKEDIN
		});

		expect(remove).toHaveBeenCalledWith('test-session', '/user/me/link/linkedin');
		expect(setSession).toHaveBeenCalledWith(
			'test-session',
			'$.currentUser',
			JSON.stringify(updatedUser)
		);
		expect(request.locals.sessionData.currentUser).toEqual(updatedUser);
	});

	it('rejects Microsoft unlink requests before calling the backend', async () => {
		const remove = vi.spyOn(backendAPI, 'delete');

		await expect(actions.unlinkaccount?.(event(IdentityProvider.MICROSOFT))).resolves.toMatchObject(
			{
				status: 400
			}
		);
		expect(remove).not.toHaveBeenCalled();
	});
});
