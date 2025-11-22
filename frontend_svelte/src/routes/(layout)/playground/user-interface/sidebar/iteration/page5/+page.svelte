<script lang="ts">
	import Title from '$components/Title.svelte';
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../Loreum.svelte';
	import Display from '$components/Display.svelte';
</script>

<Display>Page 5</Display>

<p>
	Page 5 has hierarchial contnent and id's which are linked in main sidebar - same as page 3 so far
</p>

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
