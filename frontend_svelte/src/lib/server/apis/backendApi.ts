import AppConfig from '$lib/server/config';
import { msalAuthProvider } from '$lib/server/oauth';
import type { AccessPolicy } from '$lib/types';
import { BaseAPI, type RequestBody } from './base';
import { Action } from '$lib/accessHandler';
import { fail } from '@sveltejs/kit';

const appConfig = await AppConfig.getInstance();

class BackendAPI extends BaseAPI {
	appConfig: AppConfig;
	static pathPrefix = '/api/v1';

	constructor() {
		super(msalAuthProvider, `${appConfig.backend_origin}${BackendAPI.pathPrefix}`);
		this.appConfig = appConfig;
	}

	async post(
		session_id: string | null,
		path: string,
		body: RequestBody,
		scopes: string[] = [`${appConfig.api_scope}/api.read`, `${appConfig.api_scope}/api.write`],
		options: RequestInit = {},
		headers: HeadersInit = {}
	) {
		return await super.post(session_id, path, body, scopes, options, headers);
	}

	async get(
		session_id: string | null,
		path: string,
		scopes: string[] = [`${appConfig.api_scope}/api.read`],
		options: RequestInit = {},
		headers: HeadersInit = {}
	) {
		return await super.get(session_id, path, scopes, options, headers);
	}

	async put(
		session_id: string | null,
		path: string,
		body: RequestBody,
		scopes: string[] = [`${appConfig.api_scope}/api.read`, `${appConfig.api_scope}/api.write`],
		options: RequestInit = {},
		headers: HeadersInit = {}
	) {
		return await super.put(session_id, path, body, scopes, options, headers);
	}

	async delete(
		session_id: string,
		path: string,
		scopes: string[] = [`${appConfig.api_scope}/api.read`, `${appConfig.api_scope}/api.write`],
		options: RequestInit = {},
		headers: HeadersInit = {}
	) {
		return await super.delete(session_id, path, scopes, options, headers);
	}

	async share(
		sessionId: string,
		resourceId?: string,
		identityId?: string,
		actionIn?: string,
		newActionIn?: string,
		publicAccess: boolean = false
	) {
		// Data validation:
		// action = action ? (action as Action) : undefined;
		// newAction = newAction ? (newAction as Action) : undefined;
		const action: Action | undefined = Object.values(Action).includes(actionIn as Action)
			? (actionIn as Action)
			: undefined;
		const newAction: Action | undefined = Object.values(Action).includes(newActionIn as Action)
			? (newActionIn as Action)
			: undefined;

		// console.log(
		// 	'=== routes - demo-resource - page.server - share function executed ===',
		// 	'Resource ID:' + resourceId + '\n',
		// 	'Identity ID:' + identityId + '\n',
		// 	'Action:' + action + '\n',
		// 	'New Action:' + newAction + '\n',
		// 	'Public Access:' + publicAccess + '\n'
		// );

		// Logic to decide wether to create, update or delete the access policy:
		if (!resourceId || !identityId) {
			console.error(
				'=== routes - demo-resource - page.server - Resource ID or Identity ID is missing ==='
			);
			return fail(400, { error: 'Resource ID and Identity ID are required.' });
		}
		// TBD: check if action is present, otherwise it's a delete operation
		else if (!action) {
			const response = await this.delete(
				sessionId,
				`/access/policy?resource_id=${resourceId}&identity_id=${identityId}`
			);
			if (response.status !== 200) {
				return fail(response.status, { error: response.statusText });
			}
			return {
				identityId: identityId
			};
		} else {
			const accessPolicy: AccessPolicy = {
				resource_id: resourceId,
				identity_id: identityId,
				action: action,
				new_action: newAction,
				public: publicAccess
			};
			if (!newAction) {
				const response = await this.post(sessionId, '/access/policy', JSON.stringify(accessPolicy));
				if (response.status !== 201) {
					return fail(response.status, { error: response.statusText });
				}
				const payload = await response.json();
				return {
					identityId: identityId,
					confirmedNewAction: payload.action,
					public: payload.public
				};
				// } else {
			} else if (action !== newAction) {
				const response = await this.put(sessionId, '/access/policy', JSON.stringify(accessPolicy));
				if (response.status !== 200) {
					return fail(response.status, { error: response.statusText });
				} else {
					const payload = await response.json();
					return {
						identityId: identityId,
						confirmedNewAction: payload.action,
						public: payload.public
					};
				}
			}
			// } else {
			// 	console.error(
			// 		'=== routes - demo-resource - page.server - Action and New Action are the same ==='
			// 	);
			// 	return fail(400, { error: 'Action and New Action cannot be the same.' });
			// }
		}
	}
}

export const backendAPI = new BackendAPI();
