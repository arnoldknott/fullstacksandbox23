import { render } from '@testing-library/svelte';
import { describe, expect, test } from 'vitest';

import DemoResourceCard from './DemoResourceCard.svelte';

describe('DemoResourceCard language flag', () => {
	test('supports language codes and existing locales, and hides unsupported flags', async () => {
		const demoResource = { id: 'resource-1', name: 'Resource', language: 'da' };
		const { container, rerender } = render(DemoResourceCard, { demoResource });

		expect(container.querySelector('[class~="icon-[twemoji--flag-denmark]"]')).toBeTruthy();

		await rerender({ demoResource: { ...demoResource, language: 'en-US' } });
		expect(container.querySelector('[class~="icon-[twemoji--flag-united-states]"]')).toBeTruthy();

		await rerender({ demoResource: { ...demoResource, language: 'fr-FR' } });
		expect(container.querySelector('[class*="icon-[twemoji--flag-"]')).toBeNull();
	});
});
