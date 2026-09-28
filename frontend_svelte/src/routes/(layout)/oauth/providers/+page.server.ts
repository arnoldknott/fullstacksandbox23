import { linkedinAuthProvider } from '$lib/server/oauth/linkedin';
import { msalAuthProvider } from '$lib/server/oauth/microsoft';

import type { PageServerLoad } from './$types';

async function credentialAvailable(getCredential: () => Promise<string>): Promise<boolean> {
	try {
		return Boolean(await getCredential());
	} catch {
		return false;
	}
}

export const load: PageServerLoad = async ({ locals }) => {
	const session = locals.sessionData;
	if (!session?.loggedIn) {
		return { providerAuthentication: { microsoft: false, linkedin: false } };
	}
	const [microsoft, linkedin] = await Promise.all([
		credentialAvailable(() => msalAuthProvider.getAccessToken(session.sessionId)),
		credentialAvailable(() => linkedinAuthProvider.getIdentityToken(session.sessionId))
	]);
	return { providerAuthentication: { microsoft, linkedin } };
};
