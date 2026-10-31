import '@testing-library/jest-dom/vitest';

import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import { afterEach, describe, expect, test, vi } from 'vitest';

import ZoomableImage from './ZoomableImage.svelte';

const mocks = vi.hoisted(() => {
	const map = {
		invalidateSize: vi.fn(),
		getBoundsZoom: vi.fn(() => -1),
		setMinZoom: vi.fn(),
		getMinZoom: vi.fn(() => -1),
		getZoom: vi.fn(() => -1),
		getMaxZoom: vi.fn(() => 4),
		zoomIn: vi.fn(),
		zoomOut: vi.fn(),
		on: vi.fn(),
		fitBounds: vi.fn(),
		remove: vi.fn()
	};
	const overlay = { on: vi.fn(), addTo: vi.fn() };
	overlay.on.mockReturnValue(overlay);
	return {
		map,
		overlay,
		createMap: vi.fn(() => map),
		imageOverlay: vi.fn(() => overlay),
		latLngBounds: vi.fn(() => 'image-bounds'),
		disableClickPropagation: vi.fn(),
		disableScrollPropagation: vi.fn()
	};
});

vi.mock('leaflet', () => ({
	map: mocks.createMap,
	imageOverlay: mocks.imageOverlay,
	latLngBounds: mocks.latLngBounds,
	CRS: { Simple: 'simple' },
	DomEvent: {
		disableClickPropagation: mocks.disableClickPropagation,
		disableScrollPropagation: mocks.disableScrollPropagation
	}
}));

let image: {
	onload: (() => void) | null;
	onerror: (() => void) | null;
	naturalWidth: number;
	naturalHeight: number;
	src: string;
};
let resize: ResizeObserverCallback;
const disconnect = vi.fn();

function setup() {
	vi.stubGlobal(
		'Image',
		class {
			constructor() {
				image = {
					onload: null,
					onerror: null,
					naturalWidth: 1200,
					naturalHeight: 800,
					src: ''
				};
				return image;
			}
		}
	);
	vi.stubGlobal(
		'ResizeObserver',
		class {
			constructor(callback: ResizeObserverCallback) {
				resize = callback;
			}
			observe() {}
			disconnect = disconnect;
		}
	);
}

afterEach(() => {
	vi.unstubAllGlobals();
	vi.clearAllMocks();
});

describe('ZoomableImage', () => {
	test('fits the URL image, enables wheel zoom, and cleans up on unmount', async () => {
		setup();
		const view = render(ZoomableImage, { url: '/overshoot.jpg' });
		await waitFor(() => expect(image.src).toBe('/overshoot.jpg'));
		const container = view.container.firstElementChild as HTMLElement;
		container.style.paddingBottom = '48px';
		Object.defineProperties(container, {
			clientWidth: { value: 900 },
			clientHeight: { value: 648 }
		});
		image.onload?.();

		expect(mocks.createMap).toHaveBeenCalledWith(
			expect.any(HTMLElement),
			expect.objectContaining({
				crs: 'simple',
				scrollWheelZoom: true,
				wheelPxPerZoomLevel: 3,
				keyboard: false,
				zoomControl: false
			})
		);
		expect(mocks.imageOverlay).toHaveBeenCalledWith(
			'/overshoot.jpg',
			'image-bounds',
			expect.objectContaining({ alt: 'Zoomable image' })
		);
		expect(mocks.map.fitBounds).toHaveBeenCalledWith('image-bounds', { animate: false });
		const mapElement = container.firstElementChild as HTMLElement;
		expect(mapElement.style.width).toBe('900px');
		expect(mapElement.style.height).toBe('600px');
		expect(mapElement).toHaveAttribute('data-prevent-swipe');

		mocks.map.getZoom.mockReturnValueOnce(1);
		resize([], {} as ResizeObserver);
		expect(mocks.map.fitBounds).toHaveBeenCalledTimes(1);
		const plus = await screen.findByRole('button', { name: 'Zoom in' });
		const minus = screen.getByRole('button', { name: 'Zoom out' });
		expect(minus).toBeDisabled();
		await fireEvent.click(plus);
		expect(mocks.map.zoomIn).toHaveBeenCalledOnce();
		mocks.map.getZoom.mockReturnValueOnce(1);
		const updateControls = mocks.map.on.mock.calls[0][1];
		updateControls();
		await waitFor(() => expect(minus).toBeEnabled());
		await fireEvent.click(minus);
		expect(mocks.map.zoomOut).toHaveBeenCalledOnce();
		await fireEvent.click(await screen.findByRole('button', { name: 'Reset view' }));
		expect(mocks.map.fitBounds).toHaveBeenCalledTimes(2);
		expect(mocks.map.fitBounds).toHaveBeenLastCalledWith('image-bounds', { animate: false });
		view.unmount();
		expect(mocks.map.remove).toHaveBeenCalledOnce();
		expect(disconnect).toHaveBeenCalledOnce();
		expect(image.onload).toBeNull();
	});

	test('shows image failures instead of an empty viewer', async () => {
		setup();
		const log = vi.spyOn(console, 'error').mockImplementation(() => {});
		const view = render(ZoomableImage, { url: '/missing.jpg' });
		await waitFor(() => expect(image.src).toBe('/missing.jpg'));
		image.onerror?.();
		expect(await screen.findByRole('alert')).toHaveTextContent('Unable to load this image.');
		expect(log).toHaveBeenCalled();
		expect(mocks.createMap).not.toHaveBeenCalled();
		expect(screen.queryByRole('button', { name: 'Reset view' })).not.toBeInTheDocument();
		view.unmount();
		log.mockRestore();
	});

	test('replaces the overlay when the URL changes', async () => {
		setup();
		const view = render(ZoomableImage, { url: '/first.jpg' });
		await waitFor(() => expect(image.src).toBe('/first.jpg'));
		image.onload?.();
		await view.rerender({ url: '/second.jpg' });
		await waitFor(() => expect(image.src).toBe('/second.jpg'));
		expect(mocks.map.remove).toHaveBeenCalledOnce();
		image.onload?.();
		expect(mocks.imageOverlay).toHaveBeenLastCalledWith(
			'/second.jpg',
			'image-bounds',
			expect.any(Object)
		);
		view.unmount();
	});
});
