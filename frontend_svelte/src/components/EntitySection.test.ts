import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { createRawSnippet } from 'svelte';
import { describe, expect, test } from 'vitest';

import EntitySection from './EntitySection.svelte';

const view = (content: string) =>
	createRawSnippet(() => ({
		render: () => `<p>${content}</p>`
	}));

describe('EntitySection views', () => {
	test('offers supplied views and updates when a snippet is removed', async () => {
		const { rerender } = render(EntitySection, {
			id: 'entities',
			title: 'Entities',
			entityLabel: 'entity',
			table: view('Table content'),
			preview: view('Preview content')
		});

		expect(screen.getByRole('button', { name: 'Table' })).toBeTruthy();
		expect(screen.getByRole('button', { name: 'Preview' })).toBeTruthy();
		expect(screen.queryByRole('button', { name: 'Grid' })).toBeNull();
		expect(screen.queryByRole('button', { name: 'List' })).toBeNull();
		expect(screen.getByText('Table content').closest('.hidden')).toBeNull();

		await fireEvent.click(screen.getByRole('button', { name: 'Preview' }));
		expect(screen.getByText('Preview content').closest('.hidden')).toBeNull();
		expect(screen.getByText('Table content').closest('.hidden')).toBeTruthy();

		await rerender({ preview: undefined });
		await waitFor(() => expect(screen.getByText('Table content').closest('.hidden')).toBeNull());
		expect(screen.queryByRole('button', { name: 'Table' })).toBeNull();
		expect(screen.queryByRole('button', { name: 'Preview' })).toBeNull();
	});

	test.each(['preview', 'grid', 'list', 'table'] as const)(
		'shows a single %s without a view selector',
		async (name) => {
			render(EntitySection, {
				id: 'entities',
				title: 'Entities',
				entityLabel: 'entity',
				[name]: view('Only view')
			});

			await waitFor(() => expect(screen.getByText('Only view').closest('.hidden')).toBeNull());
			expect(screen.queryByRole('button', { name: /^(Preview|Grid|List|Table)$/ })).toBeNull();
		}
	);
});
