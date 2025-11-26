<script lang="ts">
	import Title from '$components/Title.svelte';
	import Heading from '$components/Heading.svelte';
	import Loreum from '../Loreum.svelte';
	import Display from '$components/Display.svelte';
</script>

<Display
	>Changes elements for Sidebar from hard coded to Svelte components and / or Snippets</Display
>
<p>Probably drop this, as the way from hierarchy to iteration includes this anyways.</p>

<Heading id="loreum1"><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading>
<Loreum />

<Heading id="loreum2"><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading>
<Loreum />

<Heading id="sub-category">Sub Category</Heading>

<Title id="loreum3"><span class="italic">Third</span> Lorem ipsum dolor sit amet...</Title>
<Loreum />

<Title id="loreum4"><span class="italic">Fourth</span> Lorem ipsum dolor sit amet...</Title>
<Loreum />

<Heading id="loreum5"><span class="italic">Fifth</span> Lorem ipsum dolor sit amet...</Heading>
<Loreum />

<Heading id="loreum6"><span class="italic">Sixth</span> Lorem ipsum dolor sit amet...</Heading>
<Loreum />
