import { writable } from 'svelte/store';
import type { User } from 'src/types.d.ts';
// import type { PublicClientApplication } from '@azure/msal-browser';
import type { Authentication } from './oauth';

// TBD. consider moving app configuration here:
// export const configuration = writable<Configuration | undefined>();
export const auth_instance_store = writable<Authentication | undefined>(undefined);
export const user_store = writable<User | undefined>();
export const count = writable<number>(0);
