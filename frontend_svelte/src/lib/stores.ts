import { writable } from 'svelte/store';
import type { User } from 'src/types.d.ts';
import type { PublicClientApplication } from '@azure/msal-browser';

// TBD. consider moving app configuration here:
// export const configuration = writable<Configuration | undefined>();
export const msalInstanceStore = writable<PublicClientApplication | undefined>(undefined);
export const user_store = writable<User | undefined>();
export const count = writable<number>(0);
