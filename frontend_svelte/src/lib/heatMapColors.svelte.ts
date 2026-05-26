import { Hct, hexFromArgb } from '@material/material-color-utilities';
import { fromStore } from 'svelte/store';

import { themeStore } from './stores';
import { type AppTheme, Theming } from './theming';

export type HeatMapColor = {
	background: string;
	text: string;
};

export const createHeatMapColors = (
	values: number[],
	toneMultiplier: number = 1,
	format: 'hex' | 'rgb' = 'hex'
): HeatMapColor[] => {
	const theme = fromStore(themeStore);
	const activeTheme: AppTheme = theme.current;

	// for HCT:
	// red: hue = 25,
	// (yellow: hue = 104,)
	// green: hue = 130
	// use chroma and default tone from error container - always keeps the color!
	// text on it:
	// chorma and default tone always from "on error container"
	const errorHct = activeTheme.currentMode
		? Hct.fromInt(activeTheme[activeTheme.currentMode].colors.error)
		: Hct.from(25, 80, 30);
	const onErrorHct = activeTheme.currentMode
		? Hct.fromInt(activeTheme[activeTheme.currentMode].colors.onError)
		: Hct.from(24, 13, 90);
	const toneScale = Math.min(1, Math.max(0, toneMultiplier));

	let heatMapColors = values
		.map((s) => ({
			background: s * 1.05 + 25,
			text: s * 1.05 + 25
		}))
		.map((hue) => ({
			background: hexFromArgb(
				Hct.from(hue.background, errorHct.chroma, errorHct.tone * toneScale).toInt()
			),
			text: hexFromArgb(Hct.from(hue.text, onErrorHct.chroma, onErrorHct.tone * toneScale).toInt())
		}));

	if (format === 'rgb') {
		heatMapColors = heatMapColors.map((color) => ({
			background: Theming.rgbFromHex(color.background),
			text: Theming.rgbFromHex(color.text)
		}));
	}

	return heatMapColors;
};
