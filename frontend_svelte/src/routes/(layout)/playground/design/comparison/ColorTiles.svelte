<script lang="ts">
	type mdVariables = {
		background: string;
		color: string;
		name: string;
	};
	type flyonUIClasses = {
		bg: string;
		text: string;
		name: string;
	};
	let {
		materialVariables,
		flyonUIClasses
	}: { materialVariables: mdVariables; flyonUIClasses: flyonUIClasses } = $props();
</script>

<div
	class="w-84 skeleton flex h-24 items-center justify-center"
	style="background-color: var({materialVariables.background});"
>
	<p
		class="text-center text-2xl font-semibold md:text-4xl md:font-extrabold"
		style="color: var({materialVariables.color});"
	>
		{materialVariables.name}
	</p>
</div>
<div class="w-84 skeleton flex h-24 items-center justify-center {flyonUIClasses.bg}">
	<p class="text-center text-2xl font-semibold md:text-4xl md:font-extrabold {flyonUIClasses.text}">
		{flyonUIClasses.name}
	</p>
</div>
