import '@testing-library/jest-dom/vitest';

import { render } from '@testing-library/svelte';
import { createRawSnippet } from 'svelte';
import { afterAll, beforeAll, expect, test, vi } from 'vitest';

import ChatBubble from './ChatBubble.svelte';

beforeAll(() => {
	vi.stubGlobal(
		'ResizeObserver',
		class {
			observe() {}
			unobserve() {}
			disconnect() {}
		}
	);
});

afterAll(() => vi.unstubAllGlobals());

test('fragment classes preserve the positioning wrapper and oval markup', () => {
	const children = createRawSnippet(() => ({ render: () => '<span>Inner change</span>' }));
	const { container } = render(ChatBubble, {
		children,
		class: 'fragment',
		'data-fragment-index': 2,
		maxWidth: '80%'
	});
	const wrapper = container.firstElementChild;
	expect(wrapper).toHaveClass('chat-bubble-wrapper', 'fragment');
	expect(wrapper).toHaveAttribute('data-fragment-index', '2');
	expect(wrapper).toHaveAttribute('style', '--bubble-max-width: 80%;');
	expect(wrapper?.querySelector('.bubble-oval .bubble-text')).toHaveTextContent('Inner change');
});

test('ordinary custom classes also preserve the wrapper', () => {
	const children = createRawSnippet(() => ({ render: () => '<span>Content</span>' }));
	const { container } = render(ChatBubble, { children, class: 'p-8' });
	expect(container.firstElementChild).toHaveClass('chat-bubble-wrapper', 'p-8');
});
