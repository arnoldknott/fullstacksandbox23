
import { redirect } from '@sveltejs/kit';
// TBD: get from store - or wherever hooks.server.ts puts the original requested URL on where to redirect and keep "/" as default.
throw redirect(307, '/');