import AppConfig from '$lib/server/config';
import { msalAuthProvider } from '$lib/server/oauth';
import type { AccessPolicy } from '$lib/types';
import { BaseAPI, type RequestBody } from './base';

const appConfig = await AppConfig.getInstance();

class BackendAPI extends BaseAPI {
    appConfig: AppConfig;
    static pathPrefix = '/api/v1';

    constructor() {
        super(msalAuthProvider, `${appConfig.backend_origin}${BackendAPI.pathPrefix}`);
        this.appConfig = appConfig;
    }

    async post(
        session_id: string,
        path: string,
        body: RequestBody,
        scopes: string[] = [`${appConfig.api_scope}/api.read`, `${appConfig.api_scope}/api.write`],
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

    async put(
        session_id: string,
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
        accessPolicy: AccessPolicy
    ){
        console.log('=== BackendAPI - share - accessPolicy ===');
        console.log(accessPolicy);
        if (accessPolicy.action === 'unshare') {
            console.log('=== BackendAPI - share - delete ===');
			await this.delete(
				sessionId,
				`/access/policy?resource_id=${accessPolicy.resource_id}&identity_id=${accessPolicy.identity_id}`
			);
		} else {
			if (!accessPolicy.new_action) {
				{
                    console.log('=== BackendAPI - share - post ===');
					await this.post(sessionId, '/access/policy', JSON.stringify(accessPolicy));
				}
			} else {
				{
                    console.log('=== BackendAPI - share - put ===');
					await this.put(sessionId, '/access/policy', JSON.stringify(accessPolicy));
				}
			}
        }
    }
}

export const backendAPI = new BackendAPI();