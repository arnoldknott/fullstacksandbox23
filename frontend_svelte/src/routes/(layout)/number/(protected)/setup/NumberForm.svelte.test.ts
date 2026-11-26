import { fireEvent, render, screen } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';

import type { SocketIO } from '$lib/socketio.svelte';
import type { NumberExtended } from '$lib/types';

import NumberForm from './NumberForm.svelte';

vi.mock('$lib/userInterface', () => ({ initTooltip: vi.fn() }));

describe('NumberForm', () => {
	test('labels the editable fields and preserves their bindings', async () => {
		const number = $state<NumberExtended>({ id: 'number-1', value: 0 });
		render(NumberForm, { number, shareOptions: [], socketio: {} as SocketIO<NumberExtended> });

		await fireEvent.input(screen.getByLabelText('Value'), { target: { value: '42' } });
		await fireEvent.input(screen.getByLabelText('Category'), { target: { value: 'counts' } });

		expect(number).toMatchObject({ value: 42, category: 'counts' });
	});

	test('offers an optional parent-specific label and validates it separately from the category', async () => {
		const number = $state<NumberExtended>({ id: 'new_number', value: 0 });
		render(NumberForm, {
			number,
			shareOptions: [],
			socketio: {} as SocketIO<NumberExtended>,
			parentId: 'parent-1'
		});
		const label = screen.getByLabelText('Label');
		expect(label).not.toHaveAttribute('required');
		await fireEvent.input(label, { target: { value: 'vote_count' } });
		await fireEvent.input(screen.getByLabelText('Category'), { target: { value: 'Bad' } });
		expect(label).toHaveAttribute('aria-invalid', 'true');
		expect(screen.getByLabelText('Category')).toHaveAttribute('aria-invalid', 'true');
		expect(number).not.toHaveProperty('label');

		await fireEvent.input(label, { target: { value: 'vote-count' } });
		expect(label).toHaveAttribute('aria-invalid', 'false');
	});
});
