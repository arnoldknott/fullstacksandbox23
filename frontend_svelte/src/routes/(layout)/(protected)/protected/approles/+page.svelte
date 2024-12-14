<script lang="ts">
	import Title from '$components/Title.svelte';
	import '@material/web/button/filled-button.js';
	import '@material/web/switch/switch.js';

	// let selected = $state(false);
	// const toggleAIstatus = (event: Event) => {
	//     selected = !selected;
	//     console.log('selected: ' + selected);
	// }
</script>

<Title>Assign roles</Title>
<form method="POST" action="?/toggleAIuser">
	<label for="publicAIswitch"> Assign "publicAIuser" role in backendAPI to signed in user:</label>
	<!-- <input type="switch"  value={selected ? 'on': 'off' } /> -->
	<md-switch
		id="publicAIswitch"
		role="switch"
		name="publicAIstatus"
		aria-checked="false"
		tabindex="0"
		icons
	>
	</md-switch>
	<md-filled-button type="submit" role="button" tabindex="0">OK</md-filled-button>
</form>
