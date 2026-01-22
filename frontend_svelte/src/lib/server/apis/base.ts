import { type BaseOauthProvider } from '$lib/server/oauth';

export type RequestBody =
	| string
	| Blob
	| DataView
	| BufferSource
	| File
	| FormData
	| URLSearchParams
	| ReadableStream<Uint8Array>;

export class BaseAPI {
	// needs to have a method getAccessToken(session_id: string, scopes: string[]): Promise<string>;
	// which returns an access Token for the given session_id and scopes for the specific API.
	oauthProvider: BaseOauthProvider;
	apiBaseURL: string;

	constructor(oauthProvider: BaseOauthProvider, apiBaseURL: string) {
		this.oauthProvider = oauthProvider;
		this.apiBaseURL = apiBaseURL;
	}

	private constructRequest(
		path: string,
		accessToken: string | null,
		requestOptions: RequestInit = {},
		headers: HeadersInit = {}
	): Request {
		return new Request(`${this.apiBaseURL}${path}`, {
			...requestOptions,
			headers: {
				'content-type': 'application/json',
				Authorization: accessToken ? `Bearer ${accessToken}` : '',
				...requestOptions.headers,
				...headers
			}
		});
	}

	// private errorHandler(error: unknown): Response {
	// 	console.log('=== src - lib - server - apis - errorHandler ===');
	// 	console.error(error);
	// 	if (error instanceof Response) {
	// 		return error;
	// 	}
	// 	return new Response(`Error accessing ${this.apiBaseURL}`, { status: 500 });
	// }

	async post(
		session_id: string | null,
		path: string,
		body: RequestBody,
		scopes: string[] = [],
		options: RequestInit = {},
		headers: HeadersInit = {}
	): Promise<Response> {
		// try {
		const accessToken = session_id
			? await this.oauthProvider.getAccessToken(session_id, scopes)
			: null;
		// options.body = JSON.stringify(body);
		if (body instanceof FormData) {
			options.body = JSON.stringify(Object.fromEntries(body));
		} else if (typeof body === 'string') {
			options.body = body;
		} else {
			console.error('Invalid body type or not yet implemented: ' + typeof body);
			throw new Error('Invalid body type');
		}
		// options.body = body;
		options.method = 'POST';
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
		// } catch (error) {
		// 	return this.errorHandler(error);
		// }
	}

	async get(
		sessionId: string | null,
		path: string,
		scopes: string[] = [],
		options: RequestInit,
		headers: HeadersInit
	): Promise<Response> {
		// try {
		const accessToken = sessionId
			? await this.oauthProvider.getAccessToken(sessionId, scopes)
			: null;
		options.method = 'GET';
		const request = this.constructRequest(path, accessToken, options, headers);
		const response = await fetch(request);
		// if (response.status !== 200) {
		// 	console.error('=== src - lib - server - apis - get - response.status !== 200 ===');
		// 	console.error(response.status)
		// 	error(response.status, {message: 'Error accessing ' + this.apiBaseURL + path });
		// }
		return response;
		// } catch (error) {
		// 	return this.errorHandler(error);
		// }
	}

	async put(
		session_id: string | null,
		path: string,
		body: RequestBody,
		scopes: string[] = [],
		options: RequestInit = {},
		headers: HeadersInit = {}
	): Promise<Response> {
		// try {
		const accessToken = session_id
			? await this.oauthProvider.getAccessToken(session_id, scopes)
			: null;
		if (body instanceof FormData) {
			options.body = JSON.stringify(Object.fromEntries(body));
		} else if (typeof body === 'string') {
			options.body = body;
		} else {
			console.error('Invalid body type or not yet implemented: ' + typeof body);
			throw new Error('Invalid body type');
		}
		options.method = 'PUT';
		const request = this.constructRequest(path, accessToken, options, headers);
		return await fetch(request);
		// } catch (error) {
		// 	return this.errorHandler(error);
		// }
	}

	async delete(
		sessionId: string,
		path: string,
		scopes: string[] = [],
		options: RequestInit,
		headers: HeadersInit
	): Promise<Response> {
		// try {
		const accessToken = await this.oauthProvider.getAccessToken(sessionId, scopes);
		options.method = 'DELETE';
		const request = this.constructRequest(path, accessToken, options, headers);
		return await fetch(request);
		// const response = await fetch(`${this.apiBaseURL}${path}`, {
		// 	headers: {
		// 		Authorization: `Bearer ${accessToken}`
		// 	}
		// });
		// return response;
		// } catch (error) {
		// 	console.error('=== src - lib - server - apis - delete - error ===');
		// 	console.error(error);
		// 	return this.errorHandler(error);
		// }
	}
}
