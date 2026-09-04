import { render, screen } from '@testing-library/svelte';
import { type Component, createRawSnippet } from 'svelte';
import { describe, expect, it, vi } from 'vitest';

import type { EntityContainerInterface } from '$lib/entityContainer.svelte';
import type { PresentationExtended } from '$lib/types';

import Table, {
	countIcon,
	field,
	icon,
	snippet,
	type TableColumn,
	text,
	value
} from './Table.svelte';

const presentation: PresentationExtended = {
	id: 'presentation-1',
	source: 'intern',
	path: '/welcome',
	questions: []
};

const createEntityContainer = (
	overrides: Partial<EntityContainerInterface<PresentationExtended>> = {}
) =>
	({
		entities: [presentation],
		selections: {},
		addSelection: vi.fn(),
		removeSelection: vi.fn(),
		getSelectedEntities: vi.fn((name?: string) => (name ? [] : [presentation])),
		...overrides
	}) as EntityContainerInterface<PresentationExtended>;

const PresentationTable = Table as Component<{
	columns: TableColumn<PresentationExtended>[];
	entityContainer: EntityContainerInterface<PresentationExtended>;
	displaySelection?: string;
	selectionBoxes?: boolean;
}>;

describe('Table', () => {
	it('renders all header and cell configurations', () => {
		const headerSnippet = createRawSnippet(() => ({
			render: () => '<strong>Snippet header</strong>'
		}));
		const cellSnippet = createRawSnippet<[PresentationExtended]>((getEntity) => ({
			render: () => `<strong>Snippet cell: ${getEntity().source}</strong>`
		}));
		const columns: TableColumn<PresentationExtended>[] = [
			{ header: text('Path'), cell: field<PresentationExtended>('path') },
			{
				header: snippet(headerSnippet),
				cell: snippet(cellSnippet)
			},
			{
				header: countIcon('codicon:question'),
				cell: value((entity) => entity.questions?.length ?? 0)
			},
			{ header: icon('tabler:file'), cell: value(() => 'File value') }
		];

		render(PresentationTable, {
			columns,
			entityContainer: createEntityContainer(),
			selectionBoxes: false
		});

		expect(screen.getByRole('columnheader', { name: 'Path' })).toBeTruthy();
		expect(screen.getByText('Snippet header')).toBeTruthy();
		expect(screen.getAllByRole('columnheader')).toHaveLength(4);
		expect(screen.getByText('/welcome')).toBeTruthy();
		expect(screen.getByText('Snippet cell: intern')).toBeTruthy();
		expect(screen.getByText('0')).toBeTruthy();
		expect(screen.getByText('File value')).toBeTruthy();
		expect(screen.getByText('#')).toBeTruthy();
		expect(screen.queryByRole('checkbox')).toBeNull();
	});

	it('registers selection controls when selectionBoxes is enabled', () => {
		const entityContainer = createEntityContainer();
		const { unmount } = render(PresentationTable, {
			columns: [{ header: text('Path'), cell: field<PresentationExtended>('path') }],
			entityContainer
		});

		expect(screen.getAllByRole('checkbox')).toHaveLength(2);
		expect(entityContainer.addSelection).toHaveBeenCalledWith('selected');

		unmount();
		expect(entityContainer.removeSelection).toHaveBeenCalledWith('selected');
	});

	it('renders the entities from displaySelection', () => {
		const selectedPresentation: PresentationExtended = {
			...presentation,
			id: 'presentation-2',
			path: '/selected'
		};
		const entityContainer = createEntityContainer({
			getSelectedEntities: vi.fn((name?: string) =>
				name === 'visible' ? [selectedPresentation] : [presentation]
			)
		});

		render(PresentationTable, {
			columns: [{ header: text('Path'), cell: field<PresentationExtended>('path') }],
			entityContainer,
			displaySelection: 'visible',
			selectionBoxes: false
		});

		expect(screen.getByText('/selected')).toBeTruthy();
		expect(screen.queryByText('/welcome')).toBeNull();
		expect(entityContainer.getSelectedEntities).toHaveBeenCalledWith('visible');
	});
});
