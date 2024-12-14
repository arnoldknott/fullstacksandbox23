/** @type {import('tailwindcss').Config} */

import flyonui from 'flyonui';
import flyonuiPlugin from 'flyonui/plugin';

module.exports = {
	content: ['./src/**/*.{html,js,svelte,ts}', './node_modules/flyonui/dist/js/*.js'],
	theme: {
		extend: {}
	},
	darkMode: 'media',
	plugins: [flyonui, flyonuiPlugin]
};
