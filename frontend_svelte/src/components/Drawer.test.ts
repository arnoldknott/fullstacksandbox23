import { render, screen } from '@testing-library/svelte';
import { describe, expect } from 'vitest';

import { test } from '../test/fixtures';
import Drawer from './Drawer.svelte';

test.beforeEach(({ initFlyonUI }) => {
	void initFlyonUI;
});

describe('Drawer', () => {
	test('should provide a button to open the drawer', () => {
		render(Drawer);
		const openButton = screen.getByRole('button', { name: 'Open drawer' });
		expect(openButton).toBeTruthy();
	});
	test('should contain a close button', async () => {
		render(Drawer, { props: { id: 'test-drawer' } });

		const closeButton = screen.getByRole('button', { name: 'Close drawer' });
		expect(closeButton).toBeTruthy();
		expect(closeButton.getAttribute('data-overlay')).toBe('#overlay-test-drawer');
		expect(closeButton.innerHTML).toBe('<span class="icon-[tabler--x] size-5"></span>');
		expect(closeButton.className).toContain('btn');
		expect(closeButton.className).toContain('btn-circle');
		expect(closeButton.className).toContain('btn-text');
		expect(closeButton.className).toContain('btn-sm');
		expect(closeButton.className).toContain('absolute');
		expect(closeButton.className).toContain('end-3');
		expect(closeButton.className).toContain('top-3');
	});

	test('should contain an h3 header', async () => {
		render(Drawer, { props: { id: 'test-drawer', title: 'Test Drawer' } });

		const heading = screen.getByRole('heading', { level: 3 });

		expect(heading).toBeTruthy();
		expect(heading.className).toContain('drawer-title');
		expect(heading.getAttribute('id')).toBe('drawer-title-test-drawer');
		expect(heading.textContent).toBe('Test Drawer');
	});
});
