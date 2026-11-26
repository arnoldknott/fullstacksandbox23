import type { Hierarchy } from './types';

/**
 * Types of entities.
 */
export enum EntityType {
	PRESENTATION = 'presentation',
	QUESTION = 'question',
	TEXT = 'text',
	NUMBER = 'number'
}

export const isKebabCase = (value: string): boolean =>
	value.length > 0 && !/[^a-z0-9-]/.test(value);

export const getRelationshipLabel = (
	hierarchies: Hierarchy[] | undefined,
	parentId: string,
	childId: string
): string | null | undefined =>
	hierarchies?.find(
		(hierarchy) => hierarchy.parent_id === parentId && hierarchy.child_id === childId
	)?.label;

export const getLanguageFlag = (language: string | null | undefined) => {
	switch (language) {
		case 'en':
			return 'icon-[twemoji--flag-united-kingdom]';
		case 'en-US':
			return 'icon-[twemoji--flag-united-states]';
		case 'da':
		case 'da-DK':
			return 'icon-[twemoji--flag-denmark]';
		case 'de':
		case 'de-DE':
			return 'icon-[twemoji--flag-germany]';
		default:
			return undefined;
	}
};
