/** Identity providers supported by the application's outer authentication layer. */
export enum IdentityProvider {
	MICROSOFT = 'microsoft',
	LINKEDIN = 'linkedin'
}

type LinkedIdentityProviders = {
	azure_user_id?: string | null;
	linkedin_user_id?: string | null;
};

/** Microsoft takes precedence when the application user has both identities linked. */
export function preferredIdentityProvider(
	user: LinkedIdentityProviders,
	activeProvider?: IdentityProvider
): IdentityProvider | undefined {
	if (user.azure_user_id) return IdentityProvider.MICROSOFT;
	if (user.linkedin_user_id) return IdentityProvider.LINKEDIN;
	return activeProvider;
}
