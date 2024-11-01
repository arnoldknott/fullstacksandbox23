import { describe, test } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import Title from './Title.svelte';

describe('Title', () => {
	test('should contain an h1 header', async () => {
		render(Title);

		screen.getByRole('heading', { level: 1 });

		// const heading = screen.getByRole('heading', { level: 1 });

		// expect(heading).toBeTruthy();
	});
});
