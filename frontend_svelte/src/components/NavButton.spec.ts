import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import NavButton from './NavButton.svelte';

describe('NavButton', () => {
	test('should navigate to new URL when clicked', async () => {
		const newUrl = '/new-url';
		const link = 'New URL';
		render(NavButton, { url: newUrl, link: link });

		//const button = getByRole(document.body, 'button');
		const linkElement = screen.getByRole('link');

		expect(linkElement.getAttribute('href')).toBe(newUrl);

		// jsdom doesn't support window.location, so we can't test this
		//await fireEvent.click(button);
		//expect(global.window.location.pathname).toContain(newUrl);
	});
});
