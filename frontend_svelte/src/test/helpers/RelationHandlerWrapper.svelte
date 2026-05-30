<script lang="ts">
	// Test-only Svelte wrapper that mounts a single-child `RelationHandler` plus
	// the child's `SocketIO` instance inside a real Svelte runtime. Both class
	// constructors register `$effect` and read context, so they must be
	// instantiated during component initialization. Tests inject
	// `backendAPIConfiguration` via the Testing Library `context` render option
	// (see `src/test/renderRelationHandler.ts`).
	import { untrack } from 'svelte';

	import { type ChildRelationView, RelationHandler } from '$lib/relationHandler.svelte';
	import { SocketIO, type SocketioConnection } from '$lib/socketio.svelte';
	import type { AnyEntityExtended } from '$lib/types.d.ts';

	type Props = {
		parent: () => AnyEntityExtended | undefined;
		connection: SocketioConnection;
		initial?: () => AnyEntityExtended[] | undefined | null;
		entities?: AnyEntityExtended[] | undefined | null;
		defaultInherit?: boolean;
		getId?: (child: AnyEntityExtended) => string;
		onInstance: (handle: {
			socketio: SocketIO<AnyEntityExtended>;
			view: ChildRelationView<AnyEntityExtended>;
		}) => void;
	};

	let props: Props = $props();

	untrack(() => {
		const socketio = new SocketIO<AnyEntityExtended>(props.connection, {
			subscribeEntities: () => props.entities
		});
		const relation = new RelationHandler<AnyEntityExtended, { children: AnyEntityExtended }>(
			() => props.parent(),
			{
				children: {
					socketio,
					initial: () => props.initial?.(),
					getId: props.getId ? (child) => props.getId!(child) : undefined
				}
			},
			{ defaultInherit: props.defaultInherit }
		);
		props.onInstance({ socketio, view: relation.child('children') });
	});
</script>
