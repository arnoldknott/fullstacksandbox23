import { describe, test, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { createRawSnippet, type Snippet } from 'svelte';
import Guard from './Guard.svelte';
import { page } from '$app/state';

// Svelte has no way to fill slots programmatically yet,
// https://github.com/sveltejs/svelte/pull/4296

// vi.mock('$app/state', () => ({
// 	page: {
// 		subscribe: vi.fn()
// 	}
// }));

vi.mock('$app/state', () => ({
    page: {
        data: {
            session: {
                loggedIn: false // or true, depending on the test case
            }
        }
    }
}));

const protectedContent: Snippet = createRawSnippet(() => {
	return {
		render: () => `<span>Protected Content</span>`
		// setup: (element: Element) => {}
	};
});

describe('Guard', () => {
	test('should not show content as user is not logged in', () => {
		// TBD: mock $page.data.session.loggedIn instead
		// const sessionData = {
		// 	loggedIn: false
		// }
		// page.subscribe = vi.fn((callback) => {
		// 	callback({ data: { session: { loggedIn: false } } });
		// 	return () => {};
		// });
		vi.mocked(page).data.session.loggedIn = false;

		render(Guard, { props: { children: protectedContent } });

		const content = screen.queryByText('Protected Content');
		expect(content).toBe(null);
	});

	test('should show content as user is logged in', () => {
		// page.subscribe = vi.fn((callback) => {
		// 	callback({ data: { session: { loggedIn: true } } });
		// 	return () => {};
		// });
		vi.mocked(page).data.session.loggedIn = true;

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
