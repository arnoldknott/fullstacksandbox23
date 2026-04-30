<script lang="ts">
	// Test-only Svelte wrapper that mounts a SocketIO instance inside a real
	// Svelte runtime. The class constructor uses `getContext` and registers
	// `$effect`, so it must be instantiated during component initialization.
	// Tests inject `backendAPIConfiguration` via the Testing Library `context`
	// render option (see `src/test/renderSocketIO.ts`).
	import { untrack } from 'svelte';
	import {
		SocketIO,
		type SocketIODefaultHandlers,
		type SocketioConnection
	} from '$lib/socketio.svelte';
	import type { AnyEntityExtended } from '$lib/types.d.ts';

	type Props = {
		connection: SocketioConnection;
		entities?: AnyEntityExtended[] | undefined | null;
		defaultHandlers?: SocketIODefaultHandlers;
		onInstance: (instance: SocketIO<AnyEntityExtended>) => void;
	};

	let props: Props = $props();

	// Reads of `props.*` happen inside the `untrack` closure to satisfy Svelte's
	// `state_referenced_locally` rule — the wrapper deliberately captures these
	// values once at mount time. `entities` stays a closure (`subscribeEntities`)
	// so the class's internal `$effect` can mirror it reactively.
	untrack(() => {
		const instance = new SocketIO<AnyEntityExtended>(props.connection, {
			subscribeEntities: () => props.entities,
			defaultHandlers: props.defaultHandlers
		});
		props.onInstance(instance);
	});
</script>
