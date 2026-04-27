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

export type RenderSocketIOOptions = {
	connection?: SocketioConnection;
	entities?: AnyEntityExtended[] | undefined | null;
	defaultHandlers?: SocketIODefaultHandlers;
	backendAPIConfiguration?: BackendAPIConfiguration;
};

/**
 * Mount {@link SocketIOWrapper} with the supplied props and a Svelte context
 * containing `backendAPIConfiguration`. Returns the underlying Testing Library
 * `render` result plus an `instance` accessor for the constructed SocketIO.
 */
export const renderSocketIO = (options: RenderSocketIOOptions = {}) => {
	let instance: SocketIO<AnyEntityExtended> | undefined;

	const rendered = render(SocketIOWrapper, {
		props: {
			connection: options.connection ?? defaultConnection,
			entities: options.entities,
			defaultHandlers: options.defaultHandlers,
			onInstance: (created: SocketIO<AnyEntityExtended>) => {
				instance = created;
			}
		},
		context: new Map<string, unknown>([
			['backendAPIConfiguration', options.backendAPIConfiguration ?? defaultBackendAPIConfiguration]
		])
	});

	return {
		...rendered,
		get instance(): SocketIO<AnyEntityExtended> {
			if (!instance) throw new Error('SocketIO instance was not initialized');
			return instance;
		}
	};
};
