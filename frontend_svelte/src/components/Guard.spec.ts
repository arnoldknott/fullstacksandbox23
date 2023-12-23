import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { user_store } from '../lib/stores';
import Guard from './Guard.svelte';
import type { User } from 'src/types';

// Svelte has no way to fill slots programmatically yet,
// https://github.com/sveltejs/svelte/pull/4296

describe('Guard', () => {
	test.todo('should not show content as user is not logged in', () => {
		const mockedUser: User = {
			email: '',
			loggedIn: false
		};
		user_store.set(mockedUser);
		render(Guard, {
			props: {
				$$slots: {
					default: ['Protected Content']
				}
			}
		});
		//     props:
		//         $$slots: create({
		//             default: [ "Protected Content" ] })
		// })   ;
		const content = screen.getByText('Protected Content');
		expect(content).toBeFalsy;
	});
	test.todo('should show content as user is logged in', () => {});
});
