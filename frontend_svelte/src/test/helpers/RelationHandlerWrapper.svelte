<script lang="ts">
	// Test-only Svelte wrapper that mounts a single-child `RelationHandler` plus
	// the child's `SocketIO` instance inside a real Svelte runtime. Both class
	// constructors register `$effect` and read context, so they must be
	// instantiated during component initialization. Tests inject
	// `backendAPIConfiguration` via the Testing Library `context` render option
	// (see `src/test/renderRelationHandler.ts`).
	import { untrack } from 'svelte';

	import { type Relation, RelationHandler } from '$lib/relationHandler.svelte';
	import { SocketIO, type SocketioConnection } from '$lib/socketio.svelte';
	import type { AnyEntityExtended } from '$lib/types.d.ts';

	type Props = {
		parent: () => AnyEntityExtended | undefined;
		connection: SocketioConnection;
		initial?: () => AnyEntityExtended[] | undefined | null;
		entities?: AnyEntityExtended[] | undefined | null;
		defaultInherit?: boolean;
		onInstance: (handle: {
			socketio: SocketIO<AnyEntityExtended>;
			relationHandler: RelationHandler<AnyEntityExtended>;
			view: Relation;
		}) => void;
	};

	let props: Props = $props();

	untrack(() => {
		const socketio = new SocketIO<AnyEntityExtended>(props.connection, {
			// `linked` is derived from `socketio.entities`. Mirror a real page by
			// seeding entities with the union of `entities` and `initial`.
			subscribeEntities: () => {
				const fromEntities = props.entities ?? [];
				const fromInitial = props.initial?.() ?? [];
				const seen = new Set<string>();
				const merged: AnyEntityExtended[] = [];
				for (const entity of [...fromEntities, ...fromInitial]) {
					if (entity && !seen.has(entity.id)) {
						seen.add(entity.id);
						merged.push(entity);
					}
				}
				return merged;
			}
		});
		const relation = new RelationHandler(() => props.parent());
		const view = relation.addChild(
			'children',
			socketio,
			() => props.initial?.(),
			props.defaultInherit
		);
		props.onInstance({
			socketio,
			relationHandler: relation,
			view
		});
	});
</script>
