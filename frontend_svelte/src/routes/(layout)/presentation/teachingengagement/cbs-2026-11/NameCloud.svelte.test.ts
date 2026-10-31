import { render } from '@testing-library/svelte';
import { tick } from 'svelte';
import { afterEach, expect, test, vi } from 'vitest';

import NameCloud from './NameCloud.svelte';

afterEach(() => {
	vi.restoreAllMocks();
	vi.unstubAllGlobals();
});

test('random placements avoid the heading and stay within the container', async () => {
	const frames: FrameRequestCallback[] = [];
	vi.stubGlobal('requestAnimationFrame', (callback: FrameRequestCallback) => {
		frames.push(callback);
		return frames.length;
	});
	vi.stubGlobal('cancelAnimationFrame', vi.fn());
	vi.stubGlobal(
		'ResizeObserver',
		class {
			observe() {}
			disconnect() {}
		}
	);
	vi.spyOn(HTMLElement.prototype, 'clientWidth', 'get').mockReturnValue(1600);
	vi.spyOn(HTMLElement.prototype, 'clientHeight', 'get').mockReturnValue(900);
	vi.spyOn(HTMLElement.prototype, 'offsetWidth', 'get').mockReturnValue(200);
	vi.spyOn(HTMLElement.prototype, 'offsetHeight', 'get').mockReturnValue(60);
	for (let i = 0; i < 100; i++) {
		const view = render(NameCloud, {
			text: 'A participant',
			excludeWidth: 600,
			excludeHeight: 200
		});
		await tick();
		frames.splice(0).forEach((callback) => callback(0));
		const node = view.container.firstElementChild as HTMLElement;
		const left = parseFloat(node.style.left);
		const top = parseFloat(node.style.top);
		expect(left).toBeGreaterThanOrEqual(0);
		expect(left + 200).toBeLessThanOrEqual(1600);
		expect(top).toBeGreaterThanOrEqual(0);
		expect(top + 60).toBeLessThanOrEqual(900);
		expect(left + 200 <= 484 || left >= 1116 || top + 60 <= 334 || top >= 566).toBe(true);
		view.unmount();
	}
});
