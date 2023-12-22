import { writable } from 'svelte/store';
import type { User } from 'src/types.d.ts';

export const user_store = writable<User | undefined>();
export const count = writable<number>(0);
