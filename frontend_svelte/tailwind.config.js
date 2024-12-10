/** @type {import('tailwindcss').Config} */

module.exports = {
	content: ['./src/**/*.{html,js,svelte,ts}', './node_modules/flyonui/dist/js/*.js'],
	theme: {
		extend: {}
	},
	darkMode: 'media',
	plugins: [
		require('flyonui'),
		require('flyonui/plugin'),
	],
};
