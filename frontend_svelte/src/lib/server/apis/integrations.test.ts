import { describe, expect, it, vi } from 'vitest';

import type { User } from '$lib/types';

import { MicrosoftAccountLinking } from './integrations';
import { microsoftGraph } from './msgraph';

vi.mock('./msgraph', () => ({ microsoftGraph: { get: vi.fn() } }));

const user = (azureId: string | null): User => ({
	id: 'internal-user',
	azure_user_id: azureId,
	azure_tenant_id: azureId ? 'tenant' : null,
	linkedin_user_id: azureId ? null : 'subject',
	is_active: true,
	azure_groups: []
});

describe('Microsoft account lookup', () => {
	it('does not query Graph for LinkedIn-only users', async () => {
		vi.mocked(microsoftGraph.get).mockClear();
		expect(await MicrosoftAccountLinking.getUsers('session', [user(null)])).toEqual([]);
		expect(microsoftGraph.get).not.toHaveBeenCalled();
	});

	it('queries only Microsoft identifiers in a mixed collection', async () => {
		vi.mocked(microsoftGraph.get).mockResolvedValueOnce(
			new Response(JSON.stringify({ value: [{ id: 'microsoft-id' }] }))
		);
		expect(
			await MicrosoftAccountLinking.getUsers('session', [user(null), user('microsoft-id')])
		).toEqual([{ id: 'microsoft-id' }]);
		expect(microsoftGraph.get).toHaveBeenLastCalledWith(
			'session',
			"/users?$filter=(id eq 'microsoft-id')"
		);
	});
});
