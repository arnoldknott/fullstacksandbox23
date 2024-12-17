/** @type {import('tailwindcss').Config} */

import flyonui from 'flyonui';
import { lightFlyonUI, darkFlyonUI } from 'flyonui/src/theming/themes';
import flyonuiPlugin from 'flyonui/plugin';

module.exports = {
	content: ['./src/**/*.{html,js,svelte,ts}', './node_modules/flyonui/dist/js/*.js'],
	theme: {
		extend: {
			fontFamily: {
				// 'sans': ['Roboto', 'sans-serif'],
				// Works: switching to Work Sans:
				'sans': ['Work Sans', 'sans-serif'],
				'serif': ['Merriweather', 'serif'],
			}
		},
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
		themes: [
			// {
			// 	light: {
			// 		// lightFlyonUI,// the default FlyonUI theme
			// 		// override some colors:
			// 		// primary: rgb(65, 95, 145),
			// 		// 'primary-content': rgb(255, 255, 255),
			// 	},
			// },
			"light",
			"dark",
			{
				darkhc: {
					primary: '#f44336',
					// Additional customizations from FlyonUI
					// "--rounded-box": "1rem", // border-radius for large boxes
					// "--rounded-btn": "0.5rem", // border-radius for buttons
					// "--rounded-tooltip": "1.9rem", // border-radius for tooltip
					// "--animation-btn": "0.25s", // button click animation duration
					// "--animation-input": "0.2s", // input animation duration (e.g., checkboxes, switch)
					// "--btn-focus-scale": "0.95", // button scale transform on focus
					// "--border-btn": "1px", // button border width
					// "--tab-border": "1px", // tab border width
					// "--tab-radius": "0.5rem" // tab border-radius
				}
			},
		]
	}
};
