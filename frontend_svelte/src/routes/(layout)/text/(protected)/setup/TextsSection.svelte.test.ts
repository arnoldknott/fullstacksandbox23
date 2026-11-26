import { addIcon } from '@iconify/svelte';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/svelte';
import { beforeEach, describe, expect, test, vi } from 'vitest';

import NumbersSection from '../../../number/(protected)/setup/NumbersSection.svelte';
import TextsSection from './TextsSection.svelte';

const socketState = vi.hoisted(() => ({
	sockets: [] as {
		handlers: Map<string, (...args: unknown[]) => void>;
		emit: ReturnType<typeof vi.fn>;
	}[]
}));

vi.mock('$app/state', () => ({
	page: { url: new URL('http://localhost'), data: { session: { sessionId: 'session-1' } } }
}));
vi.mock('svelte/animate', () => ({ flip: () => ({ duration: 0 }) }));
vi.mock('svelte/transition', () => ({
	fade: () => ({ duration: 0 }),
	slide: () => ({ duration: 0 })
}));
vi.mock('$lib/userInterface', () => ({
	initDropdown: vi.fn(),
	initTabs: vi.fn(),
	initTooltip: vi.fn()
}));
vi.mock('socket.io-client', () => ({
	io: vi.fn(() => {
		const handlers = new Map<string, (...args: unknown[]) => void>();
		const socket = {
			handlers,
			on: (event: string, handler: (...args: unknown[]) => void) => {
				handlers.set(event, handler);
				return socket;
			},
			emit: vi.fn(),
			disconnect: vi.fn()
		};
		socketState.sockets.push(socket);
		return socket;
	})
}));

const context = () =>
	new Map<string, unknown>([
		['backendAPIConfiguration', { backendFqdn: 'localhost', socketIOPath: '/socketio/v1' }]
	]);

const rowFor = (name: string) => {
	const row = screen.getByRole('link', { name }).closest('tr');
	if (!row) throw new Error(`No table row for ${name}`);
	return row;
};

const expectMenuAlignment = async () => {
	const table = screen.getByRole('table');
	const header = within(table).getAllByRole('row')[0];
	const columnCount = within(header).getAllByRole('columnheader').length;
	await fireEvent.click(
		within(table).getByRole('button', { name: 'Toggle Menu in table header with more options' })
	);
	const menu = within(table).getAllByRole('row')[1];
	const menuColumnCount = [...menu.querySelectorAll('th')].reduce(
		(total, cell) => total + cell.colSpan,
		0
	);
	expect(menuColumnCount).toBe(columnCount);
};

describe('parent-context entity tables', () => {
	beforeEach(() => {
		socketState.sockets.length = 0;
		for (const icon of [
			'tabler:language',
			'andrsrxn:text-decrease-size',
			'andrsrxn:text-increase-size'
		]) {
			addIcon(icon, { body: '<path />' });
		}
	});

	test('shows each text label for the current parent and refreshes it after a link update', async () => {
		render(TextsSection, {
			props: {
				parentId: 'presentation-1',
				cursor: 1,
				identities: [],
				texts: [
					{
						id: 'text-1',
						content: 'Heading',
						language: 'en',
						hierarchies: [
							{ parent_id: 'text-parent', child_id: 'text-1', label: 'other-label' },
							{ parent_id: 'presentation-1', child_id: 'text-1', label: 'heading-label' }
						]
					},
					{
						id: 'text-2',
						content: 'Unlabeled text',
						hierarchies: [{ parent_id: 'presentation-1', child_id: 'text-2', label: null }]
					}
				]
			},
			context: context()
		});

		await waitFor(() => expect(screen.getByRole('columnheader', { name: 'Label' })).toBeVisible());
		expect(within(rowFor('Setup text Heading')).getByText('heading-label')).toBeVisible();
		expect(within(rowFor('Setup text Unlabeled text')).getByText('—')).toBeVisible();
		expect(screen.queryByText('other-label')).toBeNull();
		await expectMenuAlignment();

		const socket = socketState.sockets[0];
		socket.handlers.get('status')?.({
			success: 'link-updated',
			id: 'text-1',
			parent_id: 'presentation-1'
		});
		expect(socket.emit).toHaveBeenCalledWith('read', 'text-1');
		socket.handlers.get('transferred')?.({
			id: 'text-1',
			content: 'Heading',
			hierarchies: [{ parent_id: 'presentation-1', child_id: 'text-1', label: 'updated-label' }]
		});
		await waitFor(() =>
			expect(within(rowFor('Setup text Heading')).getByText('updated-label')).toBeVisible()
		);
		socket.handlers.get('transferred')?.({
			id: 'text-1',
			content: 'Heading',
			hierarchies: [{ parent_id: 'presentation-1', child_id: 'text-1', label: null }]
		});
		await waitFor(() => expect(within(rowFor('Setup text Heading')).getByText('—')).toBeVisible());
	});

	test('shows a new text label after the linked child is read', async () => {
		render(TextsSection, {
			props: { parentId: 'number-parent', cursor: 1, identities: [], texts: [] },
			context: context()
		});
		const socket = socketState.sockets[0];
		socket.handlers.get('status')?.({
			success: 'linked',
			id: 'text-new',
			parent_id: 'number-parent',
			inherit: true
		});
		expect(socket.emit).toHaveBeenCalledWith('read', 'text-new');
		socket.handlers.get('transferred')?.({
			id: 'text-new',
			content: 'New text',
			hierarchies: [{ parent_id: 'number-parent', child_id: 'text-new', label: 'new-label' }]
		});

		await waitFor(() =>
			expect(within(rowFor('Setup text New text')).getByText('new-label')).toBeVisible()
		);
	});

	test('shows each number label for the current parent, including an unlabeled link', async () => {
		render(NumbersSection, {
			props: {
				parentId: 'text-parent',
				cursor: 1,
				identities: [],
				numbers: [
					{
						id: 'number-1',
						value: 42,
						hierarchies: [
							{ parent_id: 'presentation-1', child_id: 'number-1', label: 'other-label' },
							{ parent_id: 'text-parent', child_id: 'number-1', label: 'vote-count' }
						]
					},
					{
						id: 'number-2',
						value: 7,
						hierarchies: [{ parent_id: 'text-parent', child_id: 'number-2' }]
					}
				]
			},
			context: context()
		});

		await waitFor(() => expect(screen.getByRole('columnheader', { name: 'Label' })).toBeVisible());
		expect(within(rowFor('Setup number 42')).getByText('vote-count')).toBeVisible();
		expect(within(rowFor('Setup number 7')).getByText('—')).toBeVisible();
		expect(screen.queryByText('other-label')).toBeNull();
		await expectMenuAlignment();

		const socket = socketState.sockets[0];
		socket.handlers.get('status')?.({
			success: 'link-updated',
			id: 'number-1',
			parent_id: 'text-parent'
		});
		expect(socket.emit).toHaveBeenCalledWith('read', 'number-1');
		socket.handlers.get('transferred')?.({
			id: 'number-1',
			value: 42,
			hierarchies: [{ parent_id: 'text-parent', child_id: 'number-1', label: 'updated-count' }]
		});
		await waitFor(() =>
			expect(within(rowFor('Setup number 42')).getByText('updated-count')).toBeVisible()
		);
	});
});
