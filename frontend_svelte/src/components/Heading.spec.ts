import { render, screen } from '@testing-library/svelte';
import { describe, expect, test } from 'vitest';

import Heading from './Heading.svelte';

describe('Heading', () => {
	test('should contain an h1 header', async () => {
		render(Heading);

		const heading = screen.getByRole('heading', { level: 2 });

		expect(heading).toBeTruthy();
		expect(heading.className).toContain('text-secondary');
	});
});
