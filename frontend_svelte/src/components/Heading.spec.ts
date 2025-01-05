import { describe, test } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Heading from './Heading.svelte';

describe('Title', () => {
	test('should contain an h1 header', async () => {
		render(Heading);

		screen.getByRole('heading', { level: 1 });

		// const heading = screen.getByRole('heading', { level: 1 });

		// expect(heading).toBeTruthy();
	});
});
