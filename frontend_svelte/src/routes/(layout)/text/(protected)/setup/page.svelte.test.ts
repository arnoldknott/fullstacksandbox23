import { addIcon } from '@iconify/svelte';
import { render, screen } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';

import type { TextExtended } from '$lib/types';

import TextSetupPage from './+page.svelte';
import type { PageData } from './$types';

vi.mock('$app/state', () => ({
	page: { url: new URL('http://localhost/text/setup') }
}));
vi.mock('svelte/animate', () => ({ flip: () => ({ duration: 0 }) }));
vi.mock('svelte/transition', () => ({
	fade: () => ({ duration: 0 }),
	slide: () => ({ duration: 0 })
}));
vi.mock('$lib/userInterface', () => ({ initDropdown: vi.fn(), initTooltip: vi.fn() }));
vi.mock('$lib/socketio.svelte', () => ({
	SocketIO: class {
		entities: TextExtended[];
		pendingEntities: TextExtended[] = [];
		identities = [];
		accessRights = {};
		selections: Record<string, string[]> = {};
		client = { disconnect: vi.fn() };

		constructor(_connection: unknown, configuration: { snapshot: { entities: TextExtended[] } }) {
			this.entities = configuration.snapshot.entities;
		}

		addSelection(name: string) {
			this.selections[name] = [];
		}

		removeSelection(name: string) {
			delete this.selections[name];
		}

		getSelectedEntities() {
			return this.entities;
		}
	}
}));

describe('text setup language flags', () => {
	test('renders Danish and German emoji flags for the backend language codes', () => {
		for (const icon of [
			'tabler:language',
			'andrsrxn:text-decrease-size',
			'andrsrxn:text-increase-size'
		]) {
			addIcon(icon, { body: '<path />' });
		}

		render(TextSetupPage, {
			data: {
				backendAPIConfiguration: {
					backendFqdn: 'example.test',
					restApiPath: '/api/v1',
					websocketPath: '/ws/v1',
					socketIOPath: '/socketio/v1'
				},
				showWelcome: false,
				session: {
					loggedIn: true,
					status: undefined,
					sessionOwnerProvider: undefined,
					microsoftProfile: undefined,
					linkedinProfile: undefined,
					sessionId: 'session-1',
					currentUser: undefined
				},
				payload: {
					texts: [
						{ id: 'text-da', content: 'Danish text', language: 'da' },
						{ id: 'text-de', content: 'German text', language: 'de' }
					],
					cursor: 1,
					identities: []
				}
			} satisfies PageData
		});

		expect(
			screen
				.getByText('Danish text')
				.closest('tr')
				?.querySelector('[class~="icon-[twemoji--flag-denmark]"]')
		).toBeTruthy();
		expect(
			screen
				.getByText('German text')
				.closest('tr')
				?.querySelector('[class~="icon-[twemoji--flag-germany]"]')
		).toBeTruthy();
	});
});
