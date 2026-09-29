import { redirect } from '@sveltejs/kit';

import type { PageServerLoad } from './$types';

/**
 * A request reaching this server-only fallback has no usable in-memory client session.
 * Microsoft is the default provider; client-side expiry detection selects a known provider directly.
 */
export const load: PageServerLoad = ({ url }) => {
	redirect(307, `/login/microsoft${url.search}`);
};
