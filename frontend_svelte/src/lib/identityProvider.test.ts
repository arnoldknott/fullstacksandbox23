import { describe, expect, test } from 'vitest';

import { IdentityProvider, preferredIdentityProvider } from './identityProvider';

describe('identity provider preference', () => {
	test('prefers Microsoft when both identities are linked', () => {
		expect(
			preferredIdentityProvider(
				{ azure_user_id: 'azure-id', linkedin_user_id: 'linkedin-id' },
				IdentityProvider.LINKEDIN
			)
		).toBe(IdentityProvider.MICROSOFT);
	});

	test('uses LinkedIn when it is the only linked identity', () => {
		expect(
			preferredIdentityProvider(
				{ azure_user_id: null, linkedin_user_id: 'linkedin-id' },
				IdentityProvider.MICROSOFT
			)
		).toBe(IdentityProvider.LINKEDIN);
	});

	test('uses the active provider when linked identity data is unavailable', () => {
		expect(preferredIdentityProvider({}, IdentityProvider.LINKEDIN)).toBe(
			IdentityProvider.LINKEDIN
		);
	});

	test('does not infer a provider when no identity information is available', () => {
		expect(preferredIdentityProvider({})).toBeUndefined();
	});
});
