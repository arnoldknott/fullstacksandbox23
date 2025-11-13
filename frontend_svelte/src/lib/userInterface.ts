import type { Attachment } from 'svelte/attachments';

export const initAccordion: Attachment = (node: Element) => {
	window.HSAccordion.autoInit(node);
};

export const initCollapse: Attachment = (node: Element) => {
	window.HSCollapse.autoInit(node);
};

export const initCarousel: Attachment = (node: Element) => {
	window.HSCarousel.autoInit(node);
};

export const initDropdown: Attachment = (node: Element) => {
	window.HSDropdown.autoInit(node);
};

export const initOverlay: Attachment = (node: Element) => {
	window.HSOverlay.autoInit(node);
};

export const initTabs: Attachment = (node: Element) => {
	window.HSTabs.autoInit(node);
};

export const initTooltip: Attachment = (node: Element) => {
	window.HSTooltip.autoInit(node);
};
