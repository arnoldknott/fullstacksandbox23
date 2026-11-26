import { fireEvent, render, screen } from '@testing-library/svelte';
import { describe, expect, test, vi } from 'vitest';

import type { SocketIO } from '$lib/socketio.svelte';
import type { TextExtended } from '$lib/types';

import TextForm from './TextForm.svelte';

vi.mock('$lib/userInterface', () => ({ initTooltip: vi.fn() }));

describe('TextForm', () => {
	test('labels the editable fields and preserves their bindings', async () => {
		const text = $state<TextExtended>({ id: 'text-1', content: '', language: 'en' });
		render(TextForm, { text, shareOptions: [], socketio: {} as SocketIO<TextExtended> });

		await fireEvent.input(screen.getByLabelText('Content'), { target: { value: 'Example' } });
		await fireEvent.input(screen.getByLabelText('Category'), { target: { value: 'notes' } });
		await fireEvent.input(screen.getByLabelText('Confidential'), { target: { value: 'Private' } });

		expect(text).toMatchObject({ content: 'Example', category: 'notes', confidential: 'Private' });
	});

	test('offers an optional parent-specific label and marks invalid category and label input', async () => {
		const text = $state<TextExtended>({ id: 'new_text', content: '' });
		const { rerender } = render(TextForm, {
			text,
			shareOptions: [],
			socketio: {} as SocketIO<TextExtended>,
			parentId: 'parent-1'
		});
		const label = screen.getByLabelText('Label');
		expect(label).not.toHaveAttribute('required');
		await fireEvent.input(label, { target: { value: 'Not a label' } });
		await fireEvent.input(screen.getByLabelText('Category'), { target: { value: 'Bad' } });
		expect(label).toHaveAttribute('aria-invalid', 'true');
		expect(screen.getByLabelText('Category')).toHaveAttribute('aria-invalid', 'true');
		expect(text).not.toHaveProperty('label');

		await fireEvent.input(label, { target: { value: 'heading' } });
		await fireEvent.input(screen.getByLabelText('Category'), { target: { value: '' } });
		expect(label).toHaveAttribute('aria-invalid', 'false');
		expect(screen.getByLabelText('Category')).toHaveAttribute('aria-invalid', 'false');
		await rerender({ parentId: undefined });
		expect(screen.queryByLabelText('Label')).toBeNull();
	});
});
