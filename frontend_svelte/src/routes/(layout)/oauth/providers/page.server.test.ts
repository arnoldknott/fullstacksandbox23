import { beforeEach, describe, expect, it, vi } from 'vitest';

import { linkedinAuthProvider } from '$lib/server/oauth/linkedin';
import { msalAuthProvider } from '$lib/server/oauth/microsoft';

import { load } from './+page.server';
import type { PageServerLoad } from './$types';

function event(loggedIn: boolean | null = true) {
	return {
		locals: {
			sessionData: loggedIn === null ? undefined : { loggedIn, sessionId: 'test-session' }
		}
	} as Parameters<PageServerLoad>[0];
}

describe('provider authentication status', () => {
	beforeEach(() => vi.restoreAllMocks());

	it('reports both provider credentials independently', async () => {
		vi.spyOn(msalAuthProvider, 'getAccessToken').mockResolvedValue('microsoft-token');
		vi.spyOn(linkedinAuthProvider, 'getIdentityToken').mockResolvedValue('linkedin-token');

		await expect(load(event())).resolves.toEqual({
			providerAuthentication: { microsoft: true, linkedin: true }
		});
	});

	it('reports a missing or expired provider credential without affecting the other', async () => {
		vi.spyOn(msalAuthProvider, 'getAccessToken').mockResolvedValue('microsoft-token');
		vi.spyOn(linkedinAuthProvider, 'getIdentityToken').mockRejectedValue(
			new Error('authentication expired')
		);

		await expect(load(event())).resolves.toEqual({
			providerAuthentication: { microsoft: true, linkedin: false }
		});
	});

	it('does not inspect credentials for an anonymous application session', async () => {
		const microsoft = vi.spyOn(msalAuthProvider, 'getAccessToken');
		const linkedin = vi.spyOn(linkedinAuthProvider, 'getIdentityToken');

		await expect(load(event(false))).resolves.toEqual({
			providerAuthentication: { microsoft: false, linkedin: false }
		});
		expect(microsoft).not.toHaveBeenCalled();
		expect(linkedin).not.toHaveBeenCalled();
	});

	it('handles a public request without session data', async () => {
		await expect(load(event(null))).resolves.toEqual({
			providerAuthentication: { microsoft: false, linkedin: false }
		});
	});
});
