import { writable } from 'svelte/store';
import type { User } from 'src/types.d.ts';
// import type { PublicClientApplication } from '@azure/msal-browser';
import type { Authentication } from './oauth';
import type { AccountInfo } from '@azure/msal-browser';

// TBD. consider moving app configuration here:
// export const configuration = writable<Configuration | undefined>();
export const auth_instance_store = writable<Authentication | undefined>(undefined);
export const user_store = writable<User | undefined>();
export const microsoft_account_store = writable<[AccountInfo] | undefined>(undefined);
export const count = writable<number>(0);
