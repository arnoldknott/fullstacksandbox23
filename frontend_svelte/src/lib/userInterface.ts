import type { Attachment } from 'svelte/attachments';

export const initDropdown: Attachment = (node: Element) => {
	window.HSDropdown.autoInit(node);
};

export const initOverlay: Attachment = (node: Element) => {
	window.HSOverlay.autoInit(node);
};

export const initCarousel: Attachment = (node: Element) => {
	window.HSCarousel.autoInit(node);
};

export const initTabs: Attachment = (node: Element) => {
	window.HSTabs.autoInit(node);
};
