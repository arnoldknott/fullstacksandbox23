import { writable } from 'svelte/store';
// TBD: move to a single types file:
import type { Session } from '$lib/types.d.ts';
// import type { PublicClientApplication } from '@azure/msal-browser';

// TBD. consider moving app configuration here:
// export const configuration = writable<Configuration | undefined>();
export const user_store = writable<Session | undefined>();
// export const microsoft_account_store = writable<[AccountInfo] | undefined>(undefined);
export const count = writable<number>(0);
