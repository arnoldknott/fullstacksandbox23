import { argbFromHex } from '@material/material-color-utilities';

import type { AppTheme } from '$lib/theming';

const error = argbFromHex('#B3261E');
const onError = argbFromHex('#FFFFFF');

export const defaultThemeStoreValue = {
	currentMode: 'light',
	light: {
		colors: {
			error,
			onError
		}
	} as AppTheme['light'],
	dark: {
		colors: {
			error,
			onError
		}
	} as AppTheme['dark'],
	configuration: {} as AppTheme['configuration']
} as AppTheme;
