<script lang="ts">
	import Heading from '$components/Heading.svelte';

	// let selected = $state(false);
	// const toggleAIstatus = (event: Event) => {
	//     selected = !selected;
	//     console.log('selected: ' + selected);
	// }
</script>

<Heading>Assign roles</Heading>
<form method="POST" action="?/toggleAIuser">
	<label class="label-text" for="publicAIswitch">
		Assign "publicAIuser" role in backendAPI to signed in user:</label
	>
	<input
		type="checkbox"
		class="switch switch-primary"
		id="publicAIswitch"
		name="publicAIstatus"
		aria-checked="false"
		tabindex="0"
	/>
	<button class="btn btn-primary rounded-full" type="submit" tabindex="0">OK</button>
</form>
