import { describe, expect, test } from 'vitest';

import { getLanguageFlag, isKebabCase } from './entities';

describe('isKebabCase', () => {
	test.each(['heading', 'vote-count', 'answer-42', '--'])('accepts %s', (value) => {
		expect(isKebabCase(value)).toBe(true);
	});

	test.each(['', 'Heading', 'two words', 'under_score', 'heading\n', 'æ'])(
		'rejects %j without normalizing it',
		(value) => {
			expect(isKebabCase(value)).toBe(false);
		}
	);
});

describe('getLanguageFlag', () => {
	test.each([
		['en', 'icon-[twemoji--flag-united-kingdom]'],
		['da', 'icon-[twemoji--flag-denmark]'],
		['de', 'icon-[twemoji--flag-germany]'],
		['en-US', 'icon-[twemoji--flag-united-states]'],
		['da-DK', 'icon-[twemoji--flag-denmark]'],
		['de-DE', 'icon-[twemoji--flag-germany]']
	])('maps %s to the corresponding emoji class', (language, emojiClass) => {
		expect(getLanguageFlag(language)).toBe(emojiClass);
	});

	test.each([undefined, null, '', 'fr', 'fr-FR'])('does not infer a flag for %s', (language) => {
		expect(getLanguageFlag(language)).toBeUndefined();
	});
});
