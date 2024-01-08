// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
import type { Session } from '$lib/types';

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			sessionData: Session;
		}
		// interface PageData {}
		// interface Platform {}
	}
}

export {};
