import { describe, test, expect } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Heading from './Heading.svelte';

describe('Heading', () => {
	test('should contain an h1 header', async () => {
		render(Heading);

		const heading = screen.getByRole('heading', { level: 2 });

		expect(heading).toBeTruthy();
		expect(heading.className).toContain('text-secondary');
	});
});
