import { writable } from 'svelte/store';

const count = writable<number>(0);
export default count;
