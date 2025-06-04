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
		resourceId?: string,
		identityId?: string,
		actionIn?: string,
		newActionIn?: string,
		publicAccess: boolean = false	
	) {
		// Data validation:
		let action: Action | undefined = Object.values(Action).includes(actionIn as Action) ? (actionIn as Action) : undefined;
		let newAction: Action | undefined = Object.values(Action).includes(newActionIn as Action) ? (newActionIn as Action) : undefined;

		// Logic to decide wether to create, update or delete the access policy:
		if (!resourceId || !identityId) {
			console.error('=== routes - demo-resource - page.server - Resource ID or Identity ID is missing ===');
			return fail(400, { error: 'Resource ID and Identity ID are required.' });
		} else if (action === 'unshare' || newAction === 'unshare') {
            console.log('=== routes - demo-resource - page.server - delete ===');
            await this.delete(
				sessionId,
				`/access/policy?resource_id=${resourceId}&identity_id=${identityId}`
			);
        } else {
            if ( !action && newAction) {
                action = newAction;
                newAction = undefined;
                
            }
            if (action) {
                const accessPolicy: AccessPolicy = {
                    resource_id: resourceId,
                    identity_id: identityId,
                    action: action,
                    new_action: newAction,
                    public: publicAccess
                };
                if (!newAction) {
                    console.log('=== routes - demo-resource - page.server - post ===');
                    await this.post(sessionId, '/access/policy', JSON.stringify(accessPolicy));
                } else {
                    console.log('=== routes - demo-resource - page.server - put ===');
                    await this.put(sessionId, '/access/policy', JSON.stringify(accessPolicy));
                }
            }
        }
        
        // } else if (!action) {
		// 	if (!newAction) {
		// 		console.error('=== routes - demo-resource - page.server - Action and newAction is missing ===');
		// 		return fail(400, { error: 'Invalid action parameter.' });
		// 	} else {
        //         // call POST here
		// 		console.warn('=== routes - demo-resource - page.server - Action is missing, using newAction ===');
		// 		action = newAction;
		// 		newAction = undefined;
		// 	}
		// } else if (action === 'unshare') {
        //     // call DELETE here
        // } else if (newAction) {
        //     // call PUT here
        // } else {
        //     // call POST here

		// const accessPolicy = {
		// 	resource_id: resourceId,
		// 	identity_id: identityId,
		// 	action: action,
		// 	new_action: newAction,
		// 	public: publicAccess
		// };
	}

    // async share(
    //     sessionId: string,
    //     accessPolicy: AccessPolicy
    // ){
    //     console.log('=== BackendAPI - share - accessPolicy ===');
    //     console.log(accessPolicy);
    //     if (accessPolicy.action === 'unshare') {
    //         console.log('=== BackendAPI - share - delete ===');
	// 		await this.delete(
	// 			sessionId,
	// 			`/access/policy?resource_id=${accessPolicy.resource_id}&identity_id=${accessPolicy.identity_id}`
	// 		);
	// 	} else {
	// 		if (!accessPolicy.new_action) {
	// 			{
    //                 console.log('=== BackendAPI - share - post ===');
	// 				await this.post(sessionId, '/access/policy', JSON.stringify(accessPolicy));
	// 			}
	// 		} else {
	// 			{
    //                 console.log('=== BackendAPI - share - put ===');
	// 				await this.put(sessionId, '/access/policy', JSON.stringify(accessPolicy));
	// 			}
	// 		}
    //     }
    // }
}

export const backendAPI = new BackendAPI();