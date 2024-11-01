/** @type {import('tailwindcss').Config} */
import twElements from 'tw-elements/plugin.cjs';

module.exports = {
	content: ['./src/**/*.{html,js,svelte,ts}', './node_modules/tw-elements/js/**/*.js'],
	theme: {
		extend: {}
	},
	darkMode: 'media',
	plugins: [twElements]
};
