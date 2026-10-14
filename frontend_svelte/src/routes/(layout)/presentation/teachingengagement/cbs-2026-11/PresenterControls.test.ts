import '@testing-library/jest-dom/vitest';

import { fireEvent, render, screen } from '@testing-library/svelte';
import type { RevealApi } from 'reveal.js';
import { beforeEach, describe, expect, test, vi } from 'vitest';

import { Action } from '$lib/accessHandler';
import type { SocketIO } from '$lib/socketio.svelte';
import type { QuestionExtended } from '$lib/types';

import PresenterControls from './PresenterControls.svelte';

const browser = vi.hoisted(() => ({
	url: 'https://example.org/presentation/test?presenter=true',
	session: undefined as { loggedIn: boolean; sessionId: string } | undefined
}));
vi.mock('$app/state', () => ({
	page: {
		get url() {
			return new URL(browser.url);
		},
		get data() {
			return { session: browser.session };
		}
	}
}));

function renderControls(options: { right?: Action; slideId?: string; ready?: boolean } = {}) {
	const { slideId = 'welcome', ready = true } = options;
	const right = 'right' in options ? options.right : Action.WRITE;
	const revealHandlers = new Map<string, (event?: Event) => void>();
	const socketHandlers = new Map<string, (event: unknown) => void>();
	const socketio = {
		entities: [{ id: 'state', question: 'cbs-presentation-state-books', access_right: right }],
		submitEntity: vi.fn(),
		client: {
			on: vi.fn((event, handler) => socketHandlers.set(event, handler)),
			off: vi.fn()
		}
	};
	const reveal = {
		on: vi.fn((event, handler) => revealHandlers.set(event, handler)),
		off: vi.fn(),
		isReady: () => ready,
		getCurrentSlide: () => ({ id: slideId })
	};
	const view = render(PresenterControls, {
		socketio: socketio as unknown as SocketIO<QuestionExtended>,
		revealInstance: reveal as unknown as RevealApi
	});
	const showSlide = async (id: string, event = 'slidechanged') => {
		revealHandlers.get(event)?.({ currentSlide: { id } } as unknown as Event);
	};
	return { ...view, socketio, reveal, revealHandlers, socketHandlers, showSlide };
}

beforeEach(() => {
	browser.url = 'https://example.org/presentation/test?presenter=true';
	browser.session = { loggedIn: true, sessionId: 'presenter' };
});

describe('Presenter controls', () => {
	test('welcome does not publish, and Reset changes only the state to names', async () => {
		const { socketio, rerender } = renderControls();
		expect(socketio.submitEntity).not.toHaveBeenCalled();
		await fireEvent.click(screen.getByRole('button', { name: 'Reset' }));
		expect(socketio.submitEntity).toHaveBeenCalledExactlyOnceWith(
			expect.objectContaining({ id: 'state', question: 'cbs-presentation-state-' })
		);
		await rerender({
			socketio: {
				...socketio,
				entities: [{ ...socketio.entities[0], question: 'cbs-presentation-state-' }]
			} as unknown as SocketIO<QuestionExtended>
		});
		expect(screen.queryByRole('button', { name: 'Reset' })).not.toBeInTheDocument();
		expect(screen.queryByRole('button', { name: 'Log In' })).not.toBeInTheDocument();
	});

	test('does not show Reset when the state question is already reset', () => {
		const { rerender } = renderControls();
		return rerender({
			socketio: {
				entities: [
					{ id: 'state', question: 'cbs-presentation-state-', access_right: Action.WRITE }
				],
				submitEntity: vi.fn(),
				client: { on: vi.fn(), off: vi.fn() }
			} as unknown as SocketIO<QuestionExtended>
		}).then(() => {
			expect(screen.queryByRole('button', { name: 'Reset' })).not.toBeInTheDocument();
		});
	});

	test.each([Action.READ, Action.CONNECT, undefined])(
		'never publishes or shows controls with right %s',
		async (right) => {
			const { socketio, reveal } = renderControls({ right, slideId: 'checkin-map' });
			expect(socketio.submitEntity).not.toHaveBeenCalled();
			expect(reveal.on).not.toHaveBeenCalled();
			expect(screen.queryByRole('button')).not.toBeInTheDocument();
		}
	);

	test.each(['', '?presenter=false'])('does not publish without presenter=true (%s)', (query) => {
		browser.url = `https://example.org/presentation/test${query}`;
		const { socketio, reveal } = renderControls({ slideId: 'checkin-map' });
		expect(socketio.submitEntity).not.toHaveBeenCalled();
		expect(reveal.on).not.toHaveBeenCalled();
		expect(screen.queryByRole('button')).not.toBeInTheDocument();
	});

	test('logged-out presenter mode shows Login, disables Reset and never publishes', () => {
		browser.session = undefined;
		const { socketio, reveal } = renderControls({ slideId: 'checkin-map' });
		expect(screen.getByRole('button', { name: 'Log In' })).toBeInTheDocument();
		expect(screen.getByRole('button', { name: 'Reset' })).toBeDisabled();
		expect(socketio.submitEntity).not.toHaveBeenCalled();
		expect(reveal.on).not.toHaveBeenCalled();
		const loginUrl = new URL(
			screen.getByRole('link', { name: 'Log in' }).getAttribute('href')!,
			browser.url
		);
		expect(loginUrl.searchParams.get('target-url')).toBe('/presentation/test?presenter=true');
		expect(loginUrl.searchParams.has('parent-url')).toBe(false);
	});

	test('losing write permission stops slide updates and hides Reset', async () => {
		const { socketio, reveal, revealHandlers, showSlide, rerender } = renderControls();
		await showSlide('checkin-map');
		expect(socketio.submitEntity).toHaveBeenCalledOnce();
		await rerender({
			socketio: {
				...socketio,
				entities: [{ ...socketio.entities[0], access_right: Action.READ }]
			} as unknown as SocketIO<QuestionExtended>
		});
		expect(screen.queryByRole('button')).not.toBeInTheDocument();
		expect(reveal.off).toHaveBeenCalledWith('slidechanged', revealHandlers.get('slidechanged'));
		await showSlide('comments-and-questions');
		expect(socketio.submitEntity).toHaveBeenCalledOnce();
	});

	test.each([Action.WRITE, Action.OWN])(
		'publishes relevant slides with %s and suppresses duplicates',
		async (right) => {
			const { socketio, showSlide } = renderControls({ right });
			await showSlide('checkin-map');
			await showSlide('checkin-map');
			expect(socketio.submitEntity).toHaveBeenCalledTimes(1);
			expect(socketio.submitEntity).toHaveBeenLastCalledWith(
				expect.objectContaining({ question: 'cbs-presentation-state-places' })
			);
			await showSlide('inspiration-books');
			await showSlide('comments-and-questions');
			expect(socketio.submitEntity).toHaveBeenCalledTimes(3);
			expect(socketio.submitEntity).toHaveBeenLastCalledWith(
				expect.objectContaining({ question: 'cbs-presentation-state-comments' })
			);
			await showSlide('context-courses');
			await showSlide('welcome');
			expect(socketio.submitEntity).toHaveBeenCalledTimes(3);
		}
	);

	test('handles opening directly on an interactive slide after Reveal is ready', () => {
		const { socketio } = renderControls({ slideId: 'checkin-map' });
		expect(socketio.submitEntity).toHaveBeenCalledExactlyOnceWith(
			expect.objectContaining({ question: 'cbs-presentation-state-places' })
		);
	});

	test('handles asynchronous Reveal readiness and cleans up event listeners', async () => {
		const { socketio, reveal, revealHandlers, socketHandlers, showSlide, unmount } = renderControls(
			{ ready: false }
		);
		expect(socketio.submitEntity).not.toHaveBeenCalled();
		await showSlide('checkin-map', 'ready');
		expect(socketio.submitEntity).toHaveBeenCalledOnce();
		unmount();
		expect(reveal.off).toHaveBeenCalledWith('ready', revealHandlers.get('ready'));
		expect(reveal.off).toHaveBeenCalledWith('slidechanged', revealHandlers.get('slidechanged'));
		expect(socketio.client.off).toHaveBeenCalledWith(
			'transferred',
			socketHandlers.get('transferred')
		);
		expect(socketio.client.off).toHaveBeenCalledWith('status', socketHandlers.get('status'));
	});
});
