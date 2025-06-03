import AppConfig from '$lib/server/config';
import { msalAuthProvider } from '$lib/server/oauth';
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
}

export const backendAPI = new BackendAPI();