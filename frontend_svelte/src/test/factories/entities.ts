import type { DemoResourceExtended } from '$lib/types.d.ts';

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
