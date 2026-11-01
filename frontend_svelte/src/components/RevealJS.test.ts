import { cleanup, render } from '@testing-library/svelte';
import type { RevealApi } from 'reveal.js';
import { createRawSnippet } from 'svelte';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';

import RevealJS from './RevealJS.svelte';

const mocks = vi.hoisted(() => ({
	deck: undefined as RevealApi | undefined,
	registerTarget: vi.fn<(getTarget: () => string) => () => void>(() => vi.fn())
}));
vi.mock('$lib/session', () => ({
	getSessionLifecycleContext: () => ({ registerReauthenticationTarget: mocks.registerTarget })
}));
vi.mock('reveal.js', async (importOriginal) => {
	const actual = await importOriginal<typeof import('reveal.js')>();
	return {
		...actual,
		default: vi.fn(function () {
			mocks.deck = new actual.default({});
			return mocks.deck;
		})
	};
});

const children = createRawSnippet(() => ({
	render: () => `<section>
		<section id="welcome">Welcome</section>
		<section id="inspiration-books">
			<span class="fragment">First fragment</span>
			<span class="fragment">Second fragment</span>
		</section>
	</section>`
}));

describe('resumable Reveal.js presentations', () => {
	beforeEach(() => {
		vi.useFakeTimers();
		vi.clearAllMocks();
		window.history.replaceState({}, '', '/presentation/cbs?presenter=true');
		vi.stubGlobal(
			'matchMedia',
			vi.fn(() => ({ matches: false, addEventListener: vi.fn(), removeEventListener: vi.fn() }))
		);
	});

	afterEach(async () => {
		try {
			cleanup();
			// Reveal's bundled text fitter queues window callbacks that deck.destroy() does not cancel.
			await vi.runOnlyPendingTimersAsync();
		} finally {
			// Reveal also leaves a recurring scroll-prevention interval after destroy().
			vi.clearAllTimers();
			vi.useRealTimers();
			vi.unstubAllGlobals();
			window.history.replaceState({}, '', '/');
		}
	});

	test('updates the URL and restores the same slide and fragment after a remount', async () => {
		const props = { children, options: { hash: true, fragmentInURL: true } };
		const first = render(RevealJS, { props });
		await vi.waitFor(() => expect(mocks.deck?.isReady()).toBe(true));
		mocks.deck!.slide(0, 1, 1);
		const getTarget = mocks.registerTarget.mock.calls[0][0];
		expect(getTarget()).toBe(
			`${window.location.origin}/presentation/cbs?presenter=true#/inspiration-books/1`
		);
		await vi.waitFor(() => expect(window.location.hash).toBe('#/inspiration-books/1'), {
			timeout: 2000
		});
		const returnUrl = window.location.href;
		const historyLength = window.history.length;
		first.unmount();

		const second = render(RevealJS, { props });
		try {
			await vi.waitFor(() => expect(mocks.deck?.isReady()).toBe(true));
			expect(mocks.deck?.getCurrentSlide().id).toBe('inspiration-books');
			expect(mocks.deck?.getIndices().f).toBe(1);
			expect(window.location.href).toBe(returnUrl);
			expect(window.location.search).toBe('?presenter=true');
			expect(window.history.length).toBe(historyLength);
		} finally {
			second.unmount();
		}
	});

	test('drains delayed window resize callbacks after the presentation is unmounted', async () => {
		const presentation = render(RevealJS, { props: { children } });
		await vi.waitFor(() => expect(mocks.deck?.isReady()).toBe(true));
		await vi.runOnlyPendingTimersAsync();
		const idleTimerCount = vi.getTimerCount();

		window.dispatchEvent(new Event('resize'));
		presentation.unmount();
		expect(vi.getTimerCount()).toBeGreaterThan(idleTimerCount);

		await vi.runOnlyPendingTimersAsync();
		expect(vi.getTimerCount()).toBe(idleTimerCount);
	});
});
