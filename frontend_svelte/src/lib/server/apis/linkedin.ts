import AppConfig from '$lib/server/config';
import { linkedinAuthProvider } from '$lib/server/oauth/linkedin';
import type { LinkedInProfile } from '$lib/types';

import { BaseAPI } from './base';

const appConfig = await AppConfig.getInstance();

class LinkedInAPI extends BaseAPI {
	constructor() {
		super(linkedinAuthProvider, appConfig.linkedin_api_base_uri);
	}

	async getUserInfo(sessionId: string): Promise<LinkedInProfile> {
		const response = await this.get(sessionId, '/userinfo', ['openid'], {}, {});
		if (!response.ok) {
			throw new Error(`LinkedIn UserInfo request failed with status ${response.status}.`);
		}
		const userInfo = (await response.json()) as LinkedInProfile;
		await linkedinAuthProvider.assertUserInfoSubject(sessionId, userInfo.sub);
		return userInfo;
	}
}

export const linkedInAPI = new LinkedInAPI();
