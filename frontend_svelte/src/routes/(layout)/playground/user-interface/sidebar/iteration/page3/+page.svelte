<script lang="ts">
	import Title from '$components/Title.svelte';
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../Loreum.svelte';
	import Display from '$components/Display.svelte';
</script>

<div class="bg-error-container/70 rounded-xl p-4">
	<Display>Page 3</Display>

	<p>Page 3 has hierarchial content and id's linked in main sidebar</p>

	<Heading id="loreum1"><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum />

	<Heading id="loreum2"><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum repetition={10} />

	<Heading id="loreum2a"><span class="italic">Second A</span> Lorem ipsum dolor sit amet...</Heading
	>
	<Loreum repetition={8} />

	<Heading id="sub-category">Sub Category</Heading>

	<Title id="loreum3p1"><span class="italic">3.1</span> Lorem ipsum dolor sit amet...</Title>
	<Loreum />

	<Title id="loreum3p2"><span class="italic">3.2</span> Lorem ipsum dolor sit amet...</Title>
	<Loreum />

	<Heading id="loreum4"><span class="italic">Fourth</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum />

	<Heading id="loreum5"><span class="italic">Fifth</span> Lorem ipsum dolor sit amet...</Heading>
	<Loreum repetition={20} />
</div>
