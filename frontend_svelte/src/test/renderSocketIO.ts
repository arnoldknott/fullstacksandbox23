import { render } from '@testing-library/svelte';
import type { SocketIO, SocketIODefaultHandlers, SocketioConnection } from '$lib/socketio.svelte';
import type { AnyEntityExtended, BackendAPIConfiguration } from '$lib/types.d.ts';
import SocketIOWrapper from './helpers/SocketIOWrapper.svelte';

const defaultBackendAPIConfiguration: BackendAPIConfiguration = {
	backendFqdn: 'localhost:8000',
	restApiPath: '/api/v1',
	websocketPath: '/ws/v1',
	socketIOPath: '/socketio/v1'
};

const defaultConnection: SocketioConnection = {
	namespace: '/socketio-test'
};

export type RenderSocketIOOptions<T extends AnyEntityExtended = AnyEntityExtended> = {
	connection?: SocketioConnection;
	entities?: T[] | undefined | null;
	defaultHandlers?: SocketIODefaultHandlers;
	backendAPIConfiguration?: BackendAPIConfiguration;
};

/**
 * Mount {@link SocketIOWrapper} with the supplied props and a Svelte context
 * containing `backendAPIConfiguration`. Returns the underlying Testing Library
 * `render` result plus an `instance` accessor for the constructed SocketIO.
 */
export const renderSocketIO = <T extends AnyEntityExtended = AnyEntityExtended>(
	options: RenderSocketIOOptions<T> = {}
) => {
	let instance: SocketIO<T> | undefined;

	const rendered = render(SocketIOWrapper, {
		props: {
			connection: options.connection ?? defaultConnection,
			entities: options.entities,
			defaultHandlers: options.defaultHandlers,
			onInstance: (created: SocketIO<AnyEntityExtended>) => {
				instance = created as unknown as SocketIO<T>;
			}
		},
		context: new Map<string, unknown>([
			[
				'backendAPIConfiguration',
				options.backendAPIConfiguration ?? defaultBackendAPIConfiguration
			]
		])
	});

	return {
		...rendered,
		get instance(): SocketIO<T> {
			if (!instance) throw new Error('SocketIO instance was not initialized');
			return instance;
		}
	};
};
