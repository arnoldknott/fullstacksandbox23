import type { Attachment } from 'svelte/attachments';

export const initDropdown: Attachment = (node: Element) => {
	window.HSDropdown.autoInit(node);
};
