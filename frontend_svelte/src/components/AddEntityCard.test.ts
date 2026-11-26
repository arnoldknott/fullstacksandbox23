import { fireEvent, render, screen } from '@testing-library/svelte';
import { createRawSnippet } from 'svelte';
import { describe, expect, test, vi } from 'vitest';

import { EntityType } from '$lib/entities';
import { SocketIO } from '$lib/socketio.svelte';
import type { AccessShareOption, AnyEntityExtended, TextExtended } from '$lib/types';

import AddEntityCard from './AddEntityCard.svelte';

vi.mock('$app/navigation', () => ({ goto: vi.fn() }));
vi.mock('svelte/transition', () => ({ slide: () => ({ duration: 0 }) }));
vi.mock('$lib/userInterface', () => ({ initTabs: vi.fn() }));
vi.mock('$lib/socketio.svelte', () => ({
	SocketIO: class {
		pendingEntities = [{ id: 'new_text', content: 'Text', category: '' }];
		entities = [];
		identities = [];
		accessPolicies = {};
		submitEntity = vi.fn();
		submitBulk = vi.fn();
		createPending = vi.fn();
		deleteEntity = vi.fn();
	}
}));

const form = createRawSnippet<[AnyEntityExtended, AccessShareOption[]]>(() => ({
	render: () => '<p>Text form</p>'
}));

describe('AddEntityCard validation', () => {
	test('blocks invalid category saves without clearing the pending entity and allows correction', async () => {
		const socketio = new SocketIO<TextExtended>({});
		socketio.pendingEntities[0].category = 'Bad';
		render(AddEntityCard, { socketio, entityType: EntityType.TEXT, form });
		await fireEvent.click(screen.getByRole('button', { name: 'Save text' }));
		expect(screen.getByRole('alert')).toHaveTextContent('Category must contain only');
		expect(socketio.submitBulk).not.toHaveBeenCalled();
		expect(socketio.createPending).not.toHaveBeenCalled();

		socketio.pendingEntities[0].category = '';
		await fireEvent.click(screen.getByRole('button', { name: 'Save text' }));
		expect(socketio.pendingEntities[0].category).toBeNull();
		expect(socketio.submitBulk).toHaveBeenCalledWith(undefined, false);
	});

	test.each([EntityType.TEXT, EntityType.NUMBER])(
		'does not request inheritance when creating a standalone %s',
		async (entityType) => {
			const socketio = new SocketIO<TextExtended>({});
			render(AddEntityCard, { socketio, entityType, inheritPending: true, form });
			await fireEvent.click(screen.getByRole('button', { name: `Save ${entityType}` }));
			expect(socketio.submitBulk).toHaveBeenCalledWith(undefined, false);
		}
	);

	test('preserves inheritance when creating an unlabeled child', async () => {
		const socketio = new SocketIO<TextExtended>({});
		render(AddEntityCard, {
			socketio,
			entityType: EntityType.TEXT,
			parentId: 'parent-1',
			inheritPending: true,
			form
		});
		await fireEvent.click(screen.getByRole('button', { name: 'Save text' }));
		expect(socketio.submitBulk).toHaveBeenCalledWith('parent-1', true);
	});

	test('submits a valid label for its parent without adding it to the resource', async () => {
		const socketio = new SocketIO<TextExtended>({});
		const entity = socketio.pendingEntities[0];
		render(AddEntityCard, {
			socketio,
			entityType: EntityType.TEXT,
			parentId: 'parent-1',
			labelPending: 'heading',
			inheritPending: true,
			form
		});
		await fireEvent.click(screen.getByRole('button', { name: 'Save text' }));
		expect(socketio.submitEntity).toHaveBeenCalledWith(entity, 'parent-1', true, 'heading');
		expect(socketio.submitBulk).not.toHaveBeenCalled();
		expect(entity).not.toHaveProperty('label');
	});

	test('rejects an invalid label but permits an unlabeled relationship', async () => {
		const socketio = new SocketIO<TextExtended>({});
		const { rerender } = render(AddEntityCard, {
			socketio,
			entityType: EntityType.TEXT,
			parentId: 'parent-1',
			labelPending: 'Not a label',
			form
		});
		await fireEvent.click(screen.getByRole('button', { name: 'Save text' }));
		expect(screen.getByRole('alert')).toHaveTextContent('Label must contain only');
		expect(socketio.submitEntity).not.toHaveBeenCalled();
		expect(socketio.submitBulk).not.toHaveBeenCalled();

		await rerender({ labelPending: '' });
		await fireEvent.click(screen.getByRole('button', { name: 'Save text' }));
		expect(socketio.submitBulk).toHaveBeenCalledWith('parent-1', false);
	});

	test('does not submit multiple resources with the same parent-specific label', async () => {
		const socketio = new SocketIO<TextExtended>({});
		socketio.pendingEntities.push({ id: 'new_second', content: 'Second' });
		render(AddEntityCard, {
			socketio,
			entityType: EntityType.TEXT,
			parentId: 'parent-1',
			labelPending: 'heading',
			form
		});
		await fireEvent.click(screen.getByRole('button', { name: 'Save text' }));
		expect(screen.getByRole('alert')).toHaveTextContent('Create one resource at a time');
		expect(socketio.submitEntity).not.toHaveBeenCalled();
		expect(socketio.submitBulk).not.toHaveBeenCalled();
	});
});
