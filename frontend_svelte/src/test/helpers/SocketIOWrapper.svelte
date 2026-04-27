<script lang="ts">
	// Test-only Svelte wrapper that mounts a SocketIO instance inside a real
	// Svelte runtime. The class constructor uses `getContext` and registers
	// `$effect`, so it must be instantiated during component initialization.
	// Tests inject `backendAPIConfiguration` via the Testing Library `context`
	// render option (see `src/test/renderSocketIO.ts`).
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

	let { connection, entities, defaultHandlers, onInstance }: Props = $props();

	const instance = new SocketIO<AnyEntityExtended>(connection, {
		subscribeEntities: () => entities,
		defaultHandlers
	});

	onInstance(instance);
</script>
