import { describe, it, expect } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/svelte';
import VerticalTabs from './VerticalTabs.svelte';

describe('VerticalTabs Component', () => {
	it('should render the component', () => {
		render(VerticalTabs);

		const firstTabHeading = screen.getByText(/First Tab Heading/i);

		expect(firstTabHeading).toBeTruthy();
	});
	it('should switch tabs', async () => {
		// render(VerticalTabs);

		const secondTabLink = screen.getByText(/Second Tab/i);

		fireEvent.click(secondTabLink);

		await screen.findByText(/Second Tab Heading/i);
	});
});

// describe('VerticalTabs Component', () => {
// 	it('should render the component', () => {
// 		// Create a new container for the test
// 		const host = document.createElement('div');

// 		// Append the new container in the HTML body
// 		document.body.appendChild(host);

// 		// create an instance of the vertical tab
// 		const instance = new VerticalTabs({ target: host });

// 		// Check if the instance has a value
// 		expect(instance).toBeTruthy();

// 		// Test if we can find the "First Tab Heading"
// 		expect(host.innerHTML).toContain('First Tab Heading');
// 	});
// });
