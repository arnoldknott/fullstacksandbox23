import { describe, expect, test } from 'vitest';

import { currentInput, getInputsUrl, inputEnabled, selectedInput } from './inputs';

describe('Mobile input state', () => {
	test.each([
		[
			'https://example.org/presentation/deck',
			'cbs-names',
			'https://example.org/presentation/deck/inputs?input=cbs-names'
		],
		[
			'https://example.org/presentation/deck/qrcode?input=cbs-places',
			'cbs-places',
			'https://example.org/presentation/deck/inputs?input=cbs-places'
		],
		[
			'https://example.org/presentation/deck/inputs/',
			'cbs-comments',
			'https://example.org/presentation/deck/inputs?input=cbs-comments'
		],
		[
			'https://example.org/presentation/deck/qrcode/?input=cbs-books',
			null,
			'https://example.org/presentation/deck/inputs'
		]
	])('builds canonical inputs URLs from %s', (currentUrl, input, expected) => {
		expect(getInputsUrl(new URL(currentUrl), input)).toBe(expected);
	});

	test('reads the state question without accepting unrelated question names', () => {
		expect(currentInput('cbs-presentation-state-names')).toBe('cbs-names');
		expect(currentInput('cbs-presentation-state-places')).toBe('cbs-places');
		expect(currentInput('cbs-presentation-state-books')).toBe('cbs-books');
		expect(currentInput('cbs-presentation-state-comments')).toBe('cbs-comments');
		expect(currentInput('cbs-books')).toBeUndefined();
		expect(currentInput('cbs-presentation-state-unknown')).toBeUndefined();
	});

	test('enables only current and preceding inputs, including when state moves backwards', () => {
		expect(inputEnabled('cbs-names', 'cbs-names')).toBe(true);
		expect(inputEnabled('cbs-places', 'cbs-names')).toBe(false);
		expect(inputEnabled('cbs-names', 'cbs-places')).toBe(true);
		expect(inputEnabled('cbs-places', 'cbs-books')).toBe(true);
		expect(inputEnabled('cbs-books', 'cbs-books')).toBe(true);
		expect(inputEnabled('cbs-comments', 'cbs-books')).toBe(false);
		expect(inputEnabled('cbs-books', 'cbs-places')).toBe(false);
		expect(inputEnabled('cbs-places')).toBe(false);
		expect(inputEnabled('link')).toBe(false);
		expect(inputEnabled('link', 'cbs-comments')).toBe(false);
		expect(inputEnabled('unknown', 'cbs-comments')).toBe(false);
	});

	test('honors unlocked deep links and falls back to the presenter for locked or invalid links', () => {
		expect(selectedInput('cbs-names', 'cbs-comments')).toBe('cbs-names');
		expect(selectedInput('cbs-places', 'cbs-comments')).toBe('cbs-places');
		expect(selectedInput('cbs-comments', 'cbs-places')).toBe('cbs-places');
		expect(selectedInput('unknown', 'cbs-books')).toBe('cbs-books');
		expect(selectedInput(null, 'cbs-books')).toBe('cbs-books');
		expect(selectedInput(null)).toBeUndefined();
		expect(selectedInput('link')).toBeUndefined();
		expect(selectedInput('link', 'cbs-comments')).toBe('cbs-comments');
	});
});
