<script lang="ts">
	import Title from '$components/Title.svelte';
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../Loreum.svelte';
	import Display from '$components/Display.svelte';
</script>

<div class="bg-error-container/70 rounded-xl p-4">
	<Loreum repetition={3} />
	<Display>Page 3</Display>

	<p>Page 3 has hierarchial content and id's linked in main sidebar</p>

	<Heading id="loreum1"
		><span class="italic">First</span> Lorem
		<span class="hidden sm:inline">ipsum dolor sit amet...</span></Heading
	>
	<Loreum repetition={30} />

	<Heading id="loreum2"
		><span class="italic">Second</span> Lorem
		<span class="hidden sm:inline">ipsum dolor sit amet...</span></Heading
	>
	<Loreum repetition={10} />

	<Heading id="loreum2a"
		><span class="italic">Second A</span> Lorem
		<span class="hidden sm:inline">ipsum dolor sit amet...</span></Heading
	>

	<Loreum repetition={8} />

	<Heading id="sub-category-page3">Sub Category</Heading>

	<Title id="loreum3p1"
		><span class="italic">3.1</span> Lorem
		<span class="hidden sm:inline">ipsum dolor sit amet...</span></Title
	>
	<Loreum />

	<Title id="loreum3p2"
		><span class="italic">3.2</span> Lorem
		<span class="hidden sm:inline">ipsum dolor sit amet...</span></Title
	>
	<Loreum />

	<Heading id="loreum4"
		><span class="italic">Fourth</span> Lorem
		<span class="hidden sm:inline">ipsum dolor sit amet...</span></Heading
	>
	<Loreum />

	<Heading id="loreum5"
		><span class="italic">Fifth</span> Lorem
		<span class="hidden sm:inline">ipsum dolor sit amet...</span></Heading
	>
	<Loreum repetition={20} />
</div>
