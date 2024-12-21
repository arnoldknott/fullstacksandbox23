/** @type {import('tailwindcss').Config} */

import flyonui from 'flyonui';
import { light, dark } from 'flyonui/src/theming/themes';
import flyonuiPlugin from 'flyonui/plugin';

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
				// "primary": '#F94DFF',
				// primary: 'var(--p)',
				// 'primary-content': '#9AE7FF',
				// Match accent into tertiary!
				// tertiary: '#1B82F6',
				// 'tertiary-content': '#0BEAFE',
			}
		}
		// colors: {
		// 	// This sets the default colors from TailwindCSS:
		// 	'blue-400': '#794DFF',
		// }
	},
	darkMode: 'media',
	plugins: [flyonui, flyonuiPlugin],
	flyonui: {
		// consider adding this to disable all flyonUI formating and
		// leave it to Material Design assisted by TailwindCSS
		// styled: false,
		vendors: true,
		// themeRoot: "TBD", // consider passing the theme root element here, so not all elements get themed!
		themes: [
			{
				light: {
					// ...light,
					transparent: 'transparent',
					current: 'currentColor',
					info: light.info,
					'info-content': light['info-content'],
					success: light.success,
					'success-content': light['success-content'],
			// // 		// lightFlyonUI,
			// // 		// lightFlyonUI,// the default FlyonUI theme
			// // 		// set the color object for Tailwind programmatically here - matching output from Material Dynamic Color:
			// // 		// https://github.com/themeselection/flyonui/blob/bdbdaeec6b575b80283f5fda51abd3981a168fca/src/theming/index.js#L2
			// 		transparent: 'transparent',
			// 		current: 'currentColor',
			// 		primary: '#394DFF',
			// 		// primary: 'var(--my-color)',
			// 		'primary-content': '#9AE7FF',
			// // 		// Match accent into tertiary!
			// // 		// tertiary: '#1B82F6',
			// // 		// 'tertiary-content': '#0BEAFE',
				},
			},
			{
				dark: {
					// ...dark,
					transparent: 'transparent',
					current: 'currentColor',
					info: dark.info,
					'info-content': dark['info-content'],
					success: dark.success,
					'success-content': dark['success-content'],
				}
			},
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
