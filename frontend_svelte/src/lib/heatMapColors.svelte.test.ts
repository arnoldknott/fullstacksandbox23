import { describe, expect } from 'vitest';

import { createHeatMapColors } from '$lib/heatMapColors.svelte';

import {test} from '../test/fixtures';

const inputValues = [0, 50, 100];

const expectedToneOne = [
	{ background: '#b32521', text: '#ffffff' },
	{ background: '#7e5600', text: '#ffffff' },
	{ background: '#446800', text: '#ffffff' }
];

const expectedToneHalf = [
	{ background: '#680005', text: '#7d7574' },
	{ background: '#432b00', text: '#7b7671' },
	{ background: '#213600', text: '#787773' }
];

const expectedToneZero = [
	{ background: '#000000', text: '#000000' },
	{ background: '#000000', text: '#000000' },
	{ background: '#000000', text: '#000000' }
];

const expectedRgbToneOne = [
	{ background: '179 37 33', text: '255 255 255' },
	{ background: '126 86 0', text: '255 255 255' },
	{ background: '68 104 0', text: '255 255 255' }
];

const expectedChromaHalf = [
	{ background: '#914840', text: '#ffffff' },
	{ background: '#7e5603', text: '#ffffff' },
	{ background: '#4c6625', text: '#ffffff' }
];

const expectedChromaZero = [
	{ background: '#5d5d5d', text: '#ffffff' },
	{ background: '#5d5d5d', text: '#ffffff' },
	{ background: '#5d5d5d', text: '#ffffff' }
];

const expectedChromaOnePointFive = [
	{ background: '#bf0010', text: '#ffffff' },
	{ background: '#7e5600', text: '#ffffff' },
	{ background: '#446800', text: '#ffffff' }
];


test.beforeEach(({ setThemeStore }) => {
    void setThemeStore;
});

describe('createHeatMapColors', () => {
	test('returns expected hex colors for 3 input values with mocked theme store', () => {
		expect(createHeatMapColors(inputValues)).toEqual(expectedToneOne);
	});

	test('applies toneMultiplier inside the supported 0..1 range', () => {
		expect(createHeatMapColors(inputValues, 1, 0.5)).toEqual(expectedToneHalf);
	});

	test('clamps toneMultiplier lower than 0', () => {
		expect(createHeatMapColors(inputValues, 1, -0.2)).toEqual(expectedToneZero);
	});

	test('clamps toneMultiplier higher than 1', () => {
		expect(createHeatMapColors(inputValues, 1, 2)).toEqual(expectedToneOne);
	});

	test('applies chromaMultiplier inside the supported range', () => {
		expect(createHeatMapColors(inputValues, 0.5, 1, 'hex')).toEqual(expectedChromaHalf);
	});

	test('clamps chromaMultiplier lower than 0', () => {
		expect(createHeatMapColors(inputValues, -0.2, 1, 'hex')).toEqual(expectedChromaZero);
	});

	test('allows chromaMultiplier higher than 1', () => {
		expect(createHeatMapColors(inputValues, 1.5, 1, 'hex')).toEqual(expectedChromaOnePointFive);
	});

	test("returns rgb output when format is 'rgb'", () => {
		expect(createHeatMapColors(inputValues, 1, 1, 'rgb')).toEqual(expectedRgbToneOne);
	});

	test('falls back to hex output for a gibberish format value', () => {
		const gibberishFormat = 'not-a-real-format' as unknown as 'hex';
		expect(createHeatMapColors(inputValues, 1, 1, gibberishFormat)).toEqual(expectedToneOne);
	});
});
