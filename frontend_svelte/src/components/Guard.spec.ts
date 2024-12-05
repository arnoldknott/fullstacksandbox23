import { describe, test, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { createRawSnippet, type Snippet } from 'svelte';
import Guard from './Guard.svelte';
import { page } from '$app/stores';

// Svelte has no way to fill slots programmatically yet,
// https://github.com/sveltejs/svelte/pull/4296

vi.mock('$app/stores', () => ({
	page: {
		subscribe: vi.fn()
	}
}));

const protectedContent: Snippet = createRawSnippet(() => {
	return {
		render: () => `<span>Protected Content</span>`
	};
});

// const createRawSnippet<Params extends unknown[]>(
// 	fn: (...params: Getters<Params>) => {
// 		render: () => string;
// 		setup?: (element: Element) => void | (() => void);
// 	}
// ): Snippet<Params>;

describe('Guard', () => {
	test('should not show content as user is not logged in', () => {
		// TBD: mock $page.data.session.loggedIn instead
		// const sessionData = {
		// 	loggedIn: false
		// }
		page.subscribe = vi.fn((callback) => {
			callback({ data: { session: { loggedIn: false } } });
			return () => {};
		});

		render(Guard, { props: { children: protectedContent } });

		const content = screen.queryByText('Protected Content');
		expect(content).toBe(null);
	});

	test('should show content as user is logged in', () => {
		page.subscribe = vi.fn((callback) => {
			callback({ data: { session: { loggedIn: true } } });
			return () => {};
		});

		render(Guard, { props: { children: protectedContent } });

		const content = screen.getByText('Protected Content');
		expect(content.textContent).toBe('Protected Content');
	});

	// render(Guard, {
	// 	props: {
	// 		$$slots: {
	// 			default: ['Protected Content']
	// 		}
	// 	}
	// });
	//     props:
	//         $$slots: create({
	//             default: [ "Protected Content" ] })
	// })   ;
	// 	const content = screen.getByText('Protected Content');
	// 	expect(content).toBeFalsy();
	// });
	// test.todo('should show content as user is logged in', () => {});
});
