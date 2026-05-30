import { render } from '@testing-library/svelte';

import type { Relations } from '$lib/relationHandler.svelte';
import type { SocketIO, SocketioConnection } from '$lib/socketio.svelte';
import type { AnyEntityExtended, BackendAPIConfiguration } from '$lib/types.d.ts';

import RelationHandlerWrapper from './helpers/RelationHandlerWrapper.svelte';

const defaultBackendAPIConfiguration: BackendAPIConfiguration = {
	backendFqdn: 'localhost:8000',
	restApiPath: '/api/v1',
	websocketPath: '/ws/v1',
	socketIOPath: '/socketio/v1'
};

const defaultConnection: SocketioConnection = {
	namespace: '/relation-test'
};

export type RenderRelationHandlerOptions<
	TParent extends AnyEntityExtended = AnyEntityExtended,
	TChild extends AnyEntityExtended = AnyEntityExtended
> = {
	parent?: () => TParent | undefined;
	connection?: SocketioConnection;
	initial?: () => TChild[] | undefined | null;
	entities?: TChild[] | undefined | null;
	defaultInherit?: boolean;
	backendAPIConfiguration?: BackendAPIConfiguration;
};

/**
 * Mount {@link RelationHandlerWrapper} with the supplied props and a Svelte
 * context containing `backendAPIConfiguration`. Returns the Testing Library
 * `render` result plus accessors for the constructed `SocketIO` and the
 * `Relations` view exposed by the `RelationHandler`.
 */
export const renderRelationHandler = <
	TParent extends AnyEntityExtended = AnyEntityExtended,
	TChild extends AnyEntityExtended = AnyEntityExtended
>(
	options: RenderRelationHandlerOptions<TParent, TChild> = {}
) => {
	let socketio: SocketIO<TChild> | undefined;
	let view: Relations | undefined;

	const rendered = render(RelationHandlerWrapper, {
		props: {
			parent: (options.parent ?? (() => undefined)) as () => AnyEntityExtended | undefined,
			connection: options.connection ?? defaultConnection,
			initial: options.initial as (() => AnyEntityExtended[] | undefined | null) | undefined,
			entities: options.entities as AnyEntityExtended[] | undefined | null,
			defaultInherit: options.defaultInherit,
			onInstance: (handle: { socketio: SocketIO<AnyEntityExtended>; view: Relations }) => {
				socketio = handle.socketio as unknown as SocketIO<TChild>;
				view = handle.view;
			}
		},
		context: new Map<string, unknown>([
			['backendAPIConfiguration', options.backendAPIConfiguration ?? defaultBackendAPIConfiguration]
		])
	});

	return {
		...rendered,
		get socketio(): SocketIO<TChild> {
			if (!socketio) throw new Error('SocketIO instance was not initialized');
			return socketio;
		},
		get view(): Relations {
			if (!view) throw new Error('RelationHandler view was not initialized');
			return view;
		}
	};
};
