import { render, screen } from '@testing-library/svelte';
import { describe, expect, test } from 'vitest';

import Display from './Display.svelte';

describe('Display', () => {
	test('should contain an h2 header', async () => {
		render(Display);

		const heading = screen.getByRole('heading', { level: 1 });

		expect(heading).toBeTruthy();
		expect(heading.className).toContain('text-primary');
		expect(heading.className).toContain('text-center');
	});
});
