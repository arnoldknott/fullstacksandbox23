import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Title from './Title.svelte';

describe('Title', () => {
	test('should contain an h2 header', async () => {
		render(Title);

		const heading = screen.getByRole('heading', { level: 3 });

		expect(heading).toBeTruthy();
		expect(heading.className).toContain('text-accent');
	});
});
