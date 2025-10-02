// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
import type { Session } from '$lib/types';
import type { IStaticMethods } from 'flyonui/flyonui';

declare global {
	interface Window {
		// Optional plugins
		// DataTable;
		// Dropzone;

		// FlyonUI
		HSStaticMethods: IStaticMethods;
		HSDropdown: HSDropdown;
		HSOverlay: HSOverlay;
	}

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
