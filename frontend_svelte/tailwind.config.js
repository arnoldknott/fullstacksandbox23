/** @type {import('tailwindcss').Config} */

import flyonui from 'flyonui';
// import { light, dark } from 'flyonui/src/theming/themes';
import flyonuiPlugin from 'flyonui/plugin';
import { addDynamicIconSelectors } from '@iconify/tailwind';

// const convertHexToRgb = (hex) => {
// 	const hexValue = hex.replace('#', '');
// 	const r = parseInt(hexValue.substring(0, 2), 16);
// 	const g = parseInt(hexValue.substring(2, 4), 16);
// 	const b = parseInt(hexValue.substring(4, 6), 16);
// 	console.log(`Converted hex ${hex} to rgb ${r} ${g} ${b}`);
// 	return `${r} ${g} ${b}`;
// }

module.exports = {
	content: ['./src/**/*.{html,js,svelte,ts}', './node_modules/flyonui/dist/js/*.js'],
	theme: {
		extend: {
			fontFamily: {
				// 'sans': ['Roboto', 'sans-serif'],
				// Works: switching to Work Sans:
				sans: ['Work Sans', 'sans-serif'],
				serif: ['Merriweather', 'serif']
			},
			// set the color object for Tailwind programmatically here - matching output from Material Dynamic Color:
			colors: {
				transparent: 'transparent',
				current: 'currentColor',
				// this works:
				// "primary-container": "#FF0000",
				// this also works - great!
				// "primary-container": "var(--md-sys-color-primary-container)",
				// TBD: opacity does not work yet - format needs to be 255 146 17 - no parentheses!
				// "primary-container": "var(var(--md-sys-color-primary-container)/var(--tw-bg-opacity))",
				// "primary-container": "var(--md-sys-color-primary-container)",
				// "primary-container": "var(var(--md-hex-color-primary-container)/<alpha-value>)",
				// This one works also with opacity:
				// "primary-container": "rgb(var(--md-rgb-color-primary-container))",
				// "primary-container-content": 'rgb(var(--md-rgb-color-on-primary-container))',
				// Production now - delete the experiments above again
				// FlyonUI default colors:
				primary: 'rgb(var(--md-rgb-color-primary))',
				'primary-content': 'rgb(var(--md-rgb-color-on-primary))',
				secondary: 'rgb(var(--md-rgb-color-secondary))',
				'secondary-content': 'rgb(var(--md-rgb-color-on-secondary))',
				accent: 'rgb(var(--md-rgb-color-tertiary))',
				'accent-content': 'rgb(var(--md-rgb-color-on-tertiary))',
				neutral: 'rgb(var(--md-rgb-color-neutral))',
				'neutral-content': 'rgb(var(--md-rgb-color-on-neutral))',
				info: 'rgb(var(--md-rgb-color-info))',
				'info-content': 'rgb(var(--md-rgb-color-on-info))',
				success: 'rgb(var(--md-rgb-color-success))',
				'success-content': 'rgb(var(--md-rgb-color-on-success))',
				warning: 'rgb(var(--md-rgb-color-warning))',
				'warning-content': 'rgb(var(--md-rgb-color-on-warning))',
				error: 'rgb(var(--md-rgb-color-error))',
				'error-content': 'rgb(var(--md-rgb-color-on-error))',
				'base-100': 'rgb(var(--md-rgb-color-surface-container-lowest))',
				'base-200': 'rgb(var(--md-rgb-color-surface-container))',
				'base-300': 'rgb(var(--md-rgb-color-surface-container-highest))',
				'base-content': 'rgb(var(--md-rgb-color-on-surface))',
				'base-shadow': 'rgb(var(--md-rgb-color-shadow))',
				// Material Design extensions:
				'primary-container': 'rgb(var(--md-rgb-color-primary-container))',
				'primary-container-content': 'rgb(var(--md-rgb-color-on-primary-container))',
				'secondary-container': 'rgb(var(--md-rgb-color-secondary-container))',
				'secondary-container-content': 'rgb(var(--md-rgb-color-on-secondary-container))',
				'accent-container': 'rgb(var(--md-rgb-color-tertiary-container))',
				'accent-container-content': 'rgb(var(--md-rgb-color-on-tertiary-container))',
				'neutral-container': 'rgb(var(--md-rgb-color-neutral-container))',
				'neutral-container-content': 'rgb(var(--md-rgb-color-on-neutral-container))',
				'error-container': 'rgb(var(--md-rgb-color-error-container))',
				'error-container-content': 'rgb(var(--md-rgb-color-on-error-container))',
				'warning-container': 'rgb(var(--md-rgb-color-warning-container))',
				'warning-container-content': 'rgb(var(--md-rgb-color-on-warning-container))',
				'success-container': 'rgb(var(--md-rgb-color-success-container))',
				'success-container-content': 'rgb(var(--md-rgb-color-on-success-container))',
				'info-container': 'rgb(var(--md-rgb-color-info-container))',
				'info-container-content': 'rgb(var(--md-rgb-color-on-info-container))',
				'base-150': 'rgb(var(--md-rgb-color-surface-container-low))',
				'base-250': 'rgb(var(--md-rgb-color-surface-container-high))',
				'base-content-variant': 'rgb(var(--md-rgb-color-on-surface-variant))',
				outline: 'rgb(var(--md-rgb-color-outline))',
				'outline-variant': 'rgb(var(--md-rgb-color-outline-variant))',
				'inverse-surface': 'rgb(var(--md-rgb-color-inverse-surface))',
				'inverse-surface-content': 'rgb(var(--md-rgb-color-inverse-on-surface))',
				'inverse-primary': 'rgb(var(--md-rgb-color-inverse-primary))',
				scrim: 'rgb(var(--md-rgb-color-scrim))',
				background: 'rgb(var(--md-rgb-color-background))',
				'background-content': 'rgb(var(--md-rgb-color-on-background))',
				'neutral-palette-key-color': 'rgb(var(--md-rgb-color-neutral-palette-key-color))',
				'neutral-variant-palette-key-color':
					'rgb(var(--md-rgb-color-neutral-variant-palette-key-color))',
				'primary-palette-key-color': 'rgb(var(--md-rgb-color-primary-palette-key-color))',
				'secondary-palette-key-color': 'rgb(var(--md-rgb-color-secondary-palette-key-color))',
				'accent-palette-key-color': 'rgb(var(--md-rgb-color-tertiary-palette-key-color))',
				'primary-fixed': 'rgb(var(--md-rgb-color-primary-fixed))',
				'primary-fixed-dim': 'rgb(var(--md-rgb-color-primary-fixed-dim))',
				'primary-fixed-content': 'rgb(var(--md-rgb-color-on-primary-fixed))',
				'primary-fixed-variant-content': 'rgb(var(--md-rgb-color-on-primary-fixed-variant))',
				'secondary-fixed': 'rgb(var(--md-rgb-color-secondary-fixed))',
				'secondary-fixed-dim': 'rgb(var(--md-rgb-color-secondary-fixed-dim))',
				'secondary-fixed-content': 'rgb(var(--md-rgb-color-on-secondary-fixed))',
				'secondary-fixed-variant-content': 'rgb(var(--md-rgb-color-on-secondary-fixed-variant))',
				'accent-fixed': 'rgb(var(--md-rgb-color-tertiary-fixed))',
				'accent-fixed-dim': 'rgb(var(--md-rgb-color-tertiary-fixed-dim))',
				'accent-fixed-content': 'rgb(var(--md-rgb-color-on-tertiary-fixed))',
				'accent-fixed-variant-content': 'rgb(var(--md-rgb-color-on-tertiary-fixed-variant))',
				'surface-dim': 'rgb(var(--md-rgb-color-surface-dim))',
				surface: 'rgb(var(--md-rgb-color-surface))',
				'surface-bright': 'rgb(var(--md-rgb-color-surface-bright))',
				'surface-variant': 'rgb(var(--md-rgb-color-surface-variant))',
				'surface-tint': 'rgb(var(--md-rgb-color-surface-tint))'
			}
		}
		// colors: {
		// 	// This sets the default colors from TailwindCSS:
		// 	'blue-400': '#794DFF',
		// }
	},
	darkMode: 'media',
	plugins: [flyonui, flyonuiPlugin, addDynamicIconSelectors()],
	flyonui: {
		// consider adding this to disable all flyonUI formating and
		// leave it to Material Design assisted by TailwindCSS
		// styled: false,
		vendors: true,
		// themeRoot: "TBD", // consider passing the theme root element here, so not all elements get themed!
		themes: [
			// {
			// 	light: {
			// 		...light, // TBD: remove the themes, when Material Color synchronization is fully implemented
			// 		transparent: 'transparent',
			// 		current: 'currentColor',
			// 		info: light.info,
			// 		'info-content': light['info-content'],
			// 		success: light.success,
			// 		'success-content': light['success-content']
			// 		// // 		// lightFlyonUI,
			// 		// // 		// lightFlyonUI,// the default FlyonUI theme
			// 		// // 		// set the color object for Tailwind programmatically here - matching output from Material Dynamic Color:
			// 		// // 		// https://github.com/themeselection/flyonui/blob/bdbdaeec6b575b80283f5fda51abd3981a168fca/src/theming/index.js#L2
			// 		// 		transparent: 'transparent',
			// 		// 		current: 'currentColor',
			// 		// 		primary: '#394DFF',
			// 		// 		// primary: 'var(--my-color)',
			// 		// 		'primary-content': '#9AE7FF',
			// 		// // 		// Match accent into tertiary!
			// 		// // 		// tertiary: '#1B82F6',
			// 		// // 		// 'tertiary-content': '#0BEAFE',
			// 	}
			// },
			// {
			// 	dark: {
			// 		...dark, // TBD: remove the themes, when Material Color synchronization is fully implemented
			// 		transparent: 'transparent',
			// 		current: 'currentColor',
			// 		info: dark.info,
			// 		'info-content': dark['info-content'],
			// 		success: dark.success,
			// 		'success-content': dark['success-content']
			// 	}
			// }
			// {
			// 	dark: {
			// 		darkFlyonUI,
			// 		// darkFlyonUI,// the default FlyonUI theme
			// 		// set the color object for Tailwind programmatically here - matching output from Material Dynamic Color:
			// 		//
			// 	}
			// },
			// 'light',
			// 'dark',
			// {
			// 	light: {
			// 		transparent: 'transparent',
			// 		current: 'currentColor',
			// 		light,
			// 	}
			// },
			// {
			// 	dark: {
			// 		transparent: 'transparent',
			// 		current: 'currentColor',
			// 		dark,
			// 	}
			// },
			// {
			// 	darkhc: {
			// 		primary: '#f44336'
			// 		// Additional customizations from FlyonUI
			// 		// "--rounded-box": "1rem", // border-radius for large boxes
			// 		// "--rounded-btn": "0.5rem", // border-radius for buttons
			// 		// "--rounded-tooltip": "1.9rem", // border-radius for tooltip
			// 		// "--animation-btn": "0.25s", // button click animation duration
			// 		// "--animation-input": "0.2s", // input animation duration (e.g., checkboxes, switch)
			// 		// "--btn-focus-scale": "0.95", // button scale transform on focus
			// 		// "--border-btn": "1px", // button border width
			// 		// "--tab-border": "1px", // tab border width
			// 		// "--tab-radius": "0.5rem" // tab border-radius
			// 	}
			// }
		]
	}
};
