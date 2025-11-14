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
		HSAccordion: HSAccordion;
		HSCollapse: HSCollapse;
		HSCarousel: HSCarousel;
		HSDropdown: HSDropdown;
		HSOverlay: HSOverlay;
		HSTabs: HSTabs;
		HSTooltip: HSTooltip;
		HSScrollspy: HSScrollspy;
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
