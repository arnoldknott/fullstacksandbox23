import { beforeEach, describe, expect, it, vi } from 'vitest';

const oauthMocks = vi.hoisted(() => ({
	getAccessToken: vi.fn(),
	assertUserInfoSubject: vi.fn()
}));

vi.mock('$lib/server/config', () => ({
	default: {
		getInstance: vi.fn().mockResolvedValue({
			linkedin_api_base_uri: 'https://api.linkedin.com/v2'
		})
	}
}));

vi.mock('$lib/server/oauth/linkedin', () => ({
	linkedinAuthProvider: oauthMocks
}));

import { linkedInAPI } from './linkedin';

describe('LinkedIn UserInfo', () => {
	beforeEach(() => {
		vi.restoreAllMocks();
		oauthMocks.getAccessToken.mockReset();
		oauthMocks.assertUserInfoSubject.mockReset();
	});

	it('requests /v2/userinfo with the LinkedIn access token and validates its subject', async () => {
		oauthMocks.getAccessToken.mockResolvedValue('linkedin-access-token');
		const userInfo = {
			sub: 'linkedin-subject',
			name: 'LinkedIn User',
			picture: 'https://media.example/avatar'
		};
		const fetchMock = vi
			.spyOn(globalThis, 'fetch')
			.mockResolvedValue(new Response(JSON.stringify(userInfo), { status: 200 }));

		await expect(linkedInAPI.getUserInfo('session-id')).resolves.toEqual(userInfo);

		expect(oauthMocks.getAccessToken).toHaveBeenCalledWith('session-id', ['openid']);
		const request = fetchMock.mock.calls[0][0] as Request;
		expect(request.url).toBe('https://api.linkedin.com/v2/userinfo');
		expect(request.method).toBe('GET');
		expect(request.headers.get('Authorization')).toBe('Bearer linkedin-access-token');
		expect(oauthMocks.assertUserInfoSubject).toHaveBeenCalledWith('session-id', 'linkedin-subject');
	});

	it('rejects an unsuccessful UserInfo response without accepting profile data', async () => {
		oauthMocks.getAccessToken.mockResolvedValue('linkedin-access-token');
		vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(null, { status: 401 }));

		await expect(linkedInAPI.getUserInfo('session-id')).rejects.toThrow(
			'LinkedIn UserInfo request failed with status 401.'
		);
		expect(oauthMocks.assertUserInfoSubject).not.toHaveBeenCalled();
	});
});
