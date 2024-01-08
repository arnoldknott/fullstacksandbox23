import { writable } from 'svelte/store';
import type { Session } from '$lib/types.d.ts';
// import type { PublicClientApplication } from '@azure/msal-browser';
import type { AccountInfo } from '@azure/msal-browser';

// TBD. consider moving app configuration here:
// export const configuration = writable<Configuration | undefined>();
export const user_store = writable<Session | undefined>();
export const microsoft_account_store = writable<[AccountInfo] | undefined>(undefined);
export const count = writable<number>(0);
