import AppConfig from '$lib/server/config';
import { msalAuthProvider } from '$lib/server/oauth';

const appConfig = await AppConfig.getInstance();

type RequestBody =
	| string
	| Blob
	| DataView
	| BufferSource
	| File
	| FormData
	| URLSearchParams
	| ReadableStream<Uint8Array>;

class BaseAPI {
	_getAccessToken: (sessionId: string, scopes: string[]) => Promise<string>;
	apiBaseURL: string;

	constructor(
		getAccessToken: (sessionId: string, scopes: string[]) => Promise<string>,
		apiBaseURL: string
	) {
		this._getAccessToken = getAccessToken;
		this.apiBaseURL = apiBaseURL;
	}

	private constructRequest(
		path: string,
		accessToken: string,
		requestOptions: RequestInit = {},
		headers: HeadersInit = {}
	): Request {
		return new Request(`${this.apiBaseURL}${path}`, {
			...requestOptions,
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${accessToken}`,
                ...requestOptions.headers,
				...headers
			}
		});
	}

	private errorHandler(error: unknown): Response {
		console.error(error);
		if (error instanceof Response) {
			return error;
		}
		return new Response(`Error accessing ${this.apiBaseURL}`, { status: 500 });
	}

	async post(
		session_id: string,
		path: string,
		body: RequestBody,
		scopes: string[] = [],
		options: RequestInit = {},
		headers: HeadersInit = {}
	): Promise<Response> {
		try {
			const accessToken = await this._getAccessToken(session_id, scopes);
			options.body = JSON.stringify(body);
			const request = this.constructRequest(path, accessToken, options, headers);
			return await fetch(request);
			// const response = await fetch(`${this.apiBaseURL}${path}`, {
			// 	method: 'POST',
			// 	headers: {
			// 		Authorization: `Bearer ${accessToken}`,
			// 		'Content-Type': "application/json"
			// 	},
			// 	body: JSON.stringify(body)
			// });
			// return response
		} catch (error) {
			return this.errorHandler(error);
		}
	}

	async get(
		sessionId: string,
		path: string,
		scopes: string[] = [],
		options: RequestInit,
		headers: HeadersInit
	): Promise<Response> {
		try {
			const accessToken = await this._getAccessToken(sessionId, scopes);
			const request = this.constructRequest(path, accessToken, options, headers);
			return await fetch(request);
			// const response = await fetch(`${this.apiBaseURL}${path}`, {
			// 	headers: {
			// 		Authorization: `Bearer ${accessToken}`
			// 	}
			// });
			// return response;
		} catch (error) {
			return this.errorHandler(error);
		}
	}
}

class BackendAPI extends BaseAPI {
	appConfig: AppConfig;
	static pathPrefix = '/api/v1';

	constructor() {
		super(msalAuthProvider.getAccessToken, `${appConfig.backend_origin}${BackendAPI.pathPrefix}`);
		this.appConfig = appConfig;
	}

	async post(
		session_id: string,
		path: string,
		body: RequestBody,
		scopes: string[] = [`${appConfig.api_scope}/api.write`],
		options: RequestInit = {},
		headers: HeadersInit = {}
	) {
		return await super.post(session_id, path, body, scopes, options, headers);
	}

	async get(
		session_id: string,
		path: string,
		scopes: string[] = [`${appConfig.api_scope}/api.read`],
		options: RequestInit = {},
		headers: HeadersInit = {}
	) {
		return await super.get(session_id, path, scopes, options, headers);
	}
}

export const backendAPI = new BackendAPI();

class MicrosoftGraph extends BaseAPI {
	appConfig: AppConfig;

	constructor() {
		super(msalAuthProvider.getAccessToken, appConfig.ms_graph_base_uri);
		this.appConfig = appConfig;
	}

	async post(
		sessionId: string,
		path: string,
		body: RequestBody,
		scopes: string[] = ['User.Read'],
		options: RequestInit = {},
		headers: HeadersInit = {}
	) {
		return await super.post(sessionId, path, body, scopes, options, headers);
	}

	async get(
		sessionId: string,
		path: string,
		scopes: string[] = ['User.Read'],
		options: RequestInit = {},
		headers: HeadersInit = {}
	) {
		return await super.get(sessionId, path, scopes, options, headers);
	}
}

export const microsoftGraph = new MicrosoftGraph();