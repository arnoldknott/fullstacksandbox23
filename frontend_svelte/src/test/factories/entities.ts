import type { DemoResourceExtended, GroupExtended, UeberGroupExtended } from '$lib/types.d.ts';

/**
 * Build a `DemoResourceExtended` for tests. Override any field via `overrides`.
 *
 * Place new entity-shaped factories here as the suite grows.
 */
export const createDemoResource = (
	overrides: Partial<DemoResourceExtended> = {}
): DemoResourceExtended => ({
	id: 'demo-resource-1',
	name: 'Demo Resource',
	...overrides
});

export const createGroup = (overrides: Partial<GroupExtended> = {}): GroupExtended => ({
	id: 'group-1',
	name: 'Group',
	...overrides
});

export const createUeberGroup = (
	overrides: Partial<UeberGroupExtended> = {}
): UeberGroupExtended => ({
	id: 'ueber-group-1',
	name: 'Ueber Group',
	...overrides
});
