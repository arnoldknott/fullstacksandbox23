import { fireEvent, render, screen, within } from '@testing-library/svelte';
import { afterAll, beforeAll, describe, expect, test, vi } from 'vitest';

import { Action } from '$lib/accessHandler';
import type { SocketIO } from '$lib/socketio.svelte';
import type { MessageExtended } from '$lib/types';

import Library from './Library.svelte';

vi.mock('svelte/transition', () => ({ slide: () => ({ duration: 0 }) }));
vi.mock('svelte/animate', () => ({ flip: () => ({ duration: 0 }) }));

beforeAll(() => {
	Object.defineProperty(Element.prototype, 'getAnimations', {
		configurable: true,
		value: () => []
	});
});

afterAll(() => {
	Reflect.deleteProperty(Element.prototype, 'getAnimations');
});

function renderLibrary(contents: string[] = [], names: string[] = []) {
	const pending = { id: 'new_comment', content: '', confidential: '' };
	const socketio = {
		pendingEntities: [pending],
		getSelectedEntities: vi.fn(() =>
			contents.map((content, index) => ({
				id: `answer_${index}`,
				content,
				confidential: names[index]
			}))
		),
		addPendingAccessPolicy: vi.fn(),
		submitEntity: vi.fn(),
		createPending: vi.fn()
	};
	const view = render(Library, {
		socketio: socketio as unknown as SocketIO<MessageExtended>,
		questionid: 'books-question'
	});
	return { socketio, pending, rerender: view.rerender };
}

async function openFlow() {
	await fireEvent.click(screen.getByRole('button', { name: /Csikszentmihalyi/ }));
}

describe('Library comments', () => {
	test('submits the selected book, comment and name, then clears the comment', async () => {
		const { socketio, pending } = renderLibrary();
		await openFlow();
		await fireEvent.input(screen.getByLabelText('Your Name:'), { target: { value: 'Alex' } });
		const textarea = screen.getByRole('textbox', { name: /What's your take/ });
		await fireEvent.input(textarea, { target: { value: 'A thoughtful book' } });
		await fireEvent.keyDown(textarea, { key: 'Enter' });

		expect(JSON.parse(pending.content)).toEqual({ bookdid: 'flow', comment: 'A thoughtful book' });
		expect(pending.confidential).toBe('Alex');
		expect(socketio.addPendingAccessPolicy).toHaveBeenCalledWith(pending.id, {
			public: true,
			action: Action.READ
		});
		expect(socketio.submitEntity).toHaveBeenCalledWith(pending, 'books-question', true);
		expect(socketio.createPending).toHaveBeenCalledOnce();
		expect(textarea).toHaveValue('');
	});

	test('requires a nonblank comment and defaults a blank name to Anonymous', async () => {
		const { socketio, pending } = renderLibrary();
		await openFlow();
		const textarea = screen.getByRole('textbox', { name: /What's your take/ });
		expect(textarea).toBeRequired();
		await fireEvent.keyDown(textarea, { key: 'Enter' });
		await fireEvent.input(textarea, { target: { value: '   ' } });
		await fireEvent.keyDown(textarea, { key: 'Enter' });
		expect(socketio.submitEntity).not.toHaveBeenCalled();

		await fireEvent.input(screen.getByLabelText('Your Name:'), { target: { value: '   ' } });
		await fireEvent.input(textarea, { target: { value: 'Worth reading' } });
		await fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true });
		expect(socketio.submitEntity).not.toHaveBeenCalled();
		await fireEvent.keyDown(textarea, { key: 'Enter' });
		expect(pending.confidential).toBe('Anonymous');
		expect(socketio.submitEntity).toHaveBeenCalledOnce();
	});

	test('reactively filters comments by book and ignores invalid content', async () => {
		renderLibrary(
			[
				JSON.stringify({ bookdid: 'flow', comment: 'Flow comment' }),
				JSON.stringify({ bookdid: 'pseudoarbejde', comment: 'Pseudoarbejde comment' }),
				'Legacy plain text',
				'null',
				JSON.stringify({ bookdid: 'flow', comment: 42 })
			],
			['Alex']
		);
		await openFlow();
		expect(screen.getByText('Flow comment')).toBeInTheDocument();
		const name = screen.getByText('Alex:');
		expect(name.tagName).toBe('DT');
		expect(name).toHaveClass('italic');
		expect(name.parentElement?.tagName).toBe('DL');
		expect(name.nextElementSibling).toBe(screen.getByText('Flow comment'));
		expect(screen.getByText('Flow comment').tagName).toBe('DD');
		expect(screen.queryByText('Pseudoarbejde comment')).not.toBeInTheDocument();
		expect(screen.queryByText('Legacy plain text')).not.toBeInTheDocument();

		await fireEvent.click(screen.getByRole('button', { name: /Nørmark, Dennis, & Jensen/ }));
		expect(screen.getByText('Pseudoarbejde comment')).toBeInTheDocument();
		expect(screen.getByText('Anonymous:').tagName).toBe('DT');
		expect(screen.queryByText('Flow comment')).not.toBeInTheDocument();
	});

	test('shows reactive comment counts only for books with valid comments', async () => {
		const { socketio, rerender } = renderLibrary([
			JSON.stringify({ bookdid: 'flow', comment: 'First comment' }),
			JSON.stringify({ bookdid: 'flow', comment: 'Second comment' }),
			JSON.stringify({ bookdid: 'pseudoarbejde', comment: 'Another book' }),
			JSON.stringify({ bookdid: 'flow', comment: 42 }),
			'Invalid content'
		]);
		const flowButton = screen.getByRole('button', { name: /Csikszentmihalyi/ });
		const flow = flowButton.parentElement!;
		const pseudoarbejde = screen.getByRole('button', {
			name: /Nørmark, Dennis, & Jensen/
		}).parentElement!;
		const noComments = screen.getByRole('button', { name: /Ravn, Ib/ }).parentElement!;
		expect(flow).toHaveClass('indicator');
		expect(within(flow).getByLabelText('2 comments')).toHaveTextContent('2');
		expect(within(flow).getByLabelText('2 comments')).toHaveClass('indicator-item', 'badge');
		expect(within(flowButton).queryByLabelText('2 comments')).not.toBeInTheDocument();
		expect(within(pseudoarbejde).getByLabelText('1 comment')).toHaveTextContent('1');
		expect(within(noComments).queryByLabelText(/comments?/)).not.toBeInTheDocument();

		socketio.getSelectedEntities.mockReturnValue([
			{
				id: 'updated',
				content: JSON.stringify({ bookdid: 'flow', comment: 'Remaining' }),
				confidential: ''
			}
		]);
		await rerender({ socketio: { ...socketio } as unknown as SocketIO<MessageExtended> });
		expect(within(flow).getByLabelText('1 comment')).toHaveTextContent('1');
		expect(within(pseudoarbejde).queryByLabelText(/comments?/)).not.toBeInTheDocument();
	});
});
