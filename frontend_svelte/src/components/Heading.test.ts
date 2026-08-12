import { render, screen } from '@testing-library/svelte';
import { createRawSnippet } from 'svelte';
import { describe, expect, test, vi } from 'vitest';

import type { SidebarItemContent } from '$lib/types';

// import { test } from '../test/fixtures.svelte';
import Heading from './Heading.svelte';

const { mockOnThisPageLinks } = vi.hoisted(() => ({
	mockOnThisPageLinks: [] as SidebarItemContent[]
}));

vi.mock('$lib/contexts/sidebar.svelte', async (importOriginal) => {
	const actual = await importOriginal<typeof import('$lib/contexts/sidebar.svelte')>();

	return {
		...actual,
		getOnThisPageLinks: () => mockOnThisPageLinks
	};
});

const headingContentSnippet = createRawSnippet(() => ({
	render: () => '<div>Heading Dummy title</div>'
}));

// test.beforeEach(({ setSidebarContext }) => {
// 	mockOnThisPageLinks.length = 0;
// 	mockOnThisPageLinks.push(...setSidebarContext);
// });

describe('Heading', () => {
	test('should contain an h2 header', async () => {
		render(Heading, { props: { children: headingContentSnippet, id: 'test-heading' } });

		const heading = screen.getByRole('heading', { level: 2 });

		expect(heading).toBeTruthy();
		expect(heading.className).toContain('text-primary');
		expect(heading.className).toContain('tracking-wider');
		expect(heading.className).toContain('heading-small');
		expect(heading.className).toContain('md:heading');
		expect(heading.className).toContain('lg:heading-large');
		expect(heading.className).toContain('mt-0');
		expect(heading.className).toContain('tracking-wider');

		expect(heading.textContent).toBe('Heading Dummy title');

		expect(heading.getAttribute('id')).toBe('test-heading');
	});
	test('applies extra classes', async () => {
		const { container } = render(Heading, {
			props: { children: headingContentSnippet, id: 'test-heading-with-class', class: 'italic' }
		});

		const wrapperDiv = container.firstElementChild as HTMLDivElement | null;

		expect(wrapperDiv).toBeTruthy();
		expect(wrapperDiv?.className).toContain('flex');
		expect(wrapperDiv?.className).toContain('flex-row');
		expect(wrapperDiv?.className).toContain('mt-20');
		expect(wrapperDiv?.className).toContain('italic');
	});
});
