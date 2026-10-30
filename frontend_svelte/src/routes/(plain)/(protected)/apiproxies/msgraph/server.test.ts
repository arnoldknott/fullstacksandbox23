import { error } from '@sveltejs/kit';
import { describe, expect, test, vi } from 'vitest';

const mocks = vi.hoisted(() => ({ get: vi.fn() }));
vi.mock('$lib/server/apis/msgraph', () => ({ microsoftGraph: { get: mocks.get } }));

import { GET } from './+server';

describe('Microsoft Graph proxy authentication', () => {
	test('preserves reauthentication failures instead of hiding them as server errors', async () => {
		mocks.get.mockImplementation(() => error(401, 'Reauthentication required'));

		await expect(
			GET({
				locals: { sessionData: { sessionId: 'session' } },
				url: new URL('https://app.example/apiproxies/msgraph?endpoint=/me/photo/$value'),
				setHeaders: vi.fn()
			} as never)
		).rejects.toMatchObject({ status: 401 });
	});
});
