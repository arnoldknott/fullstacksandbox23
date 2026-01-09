<script lang="ts">
	import Title from '$components/Title.svelte';
	import Heading from '$components/Heading.svelte';
	import Loreum from '../../Loreum.svelte';
	import Display from '$components/Display.svelte';
</script>

<div class="bg-error-container/70 rounded-xl p-4">
	<Loreum repetition={30} />
	<Display>Page 3</Display>

	<p>Page 3 has hierarchial content and id's linked in main sidebar</p>

	<div id="pg3loreum1">
		<Heading id="pg3loreum1title"
			><span class="italic">First</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum repetition={30} />
	</div>

	<div id="pg3loreum2">
		<Heading id="pg3loreum2title"
			><span class="italic">Second</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum repetition={10} />
	</div>

	<div id="pg3loreum2a">
		<Heading id="pg3loreum2atitle"
			><span class="italic">Second A</span> Lorem ipsum dolor sit amet...</Heading
		>
		<Loreum repetition={8} />
	</div>

	<Heading id="pg3sub-category">Sub Category</Heading>

	<div id="pg3loreum3p1">
		<Title id="pg3loreum3p1title"
			><span class="italic">3.1</span> Lorem ipsum dolor sit amet...</Title
		>
		<Loreum />
	</div>

	<div id="pg3loreum3p2">
		<Title id="pg3loreum3p2title"
			><span class="italic">3.2</span> Lorem ipsum dolor sit amet...</Title
		>
		<Loreum />
	</div>

	<div id="pg3loreum4">
		<Heading id="pg3loreum4title"
			><span class="italic">Fourth</span> Lorem ipsum dolor sit amet...
		</Heading>
		<Loreum />
	</div>

	<div id="pg3loreum5">
		<Heading id="pg3loreum5title"
			><span class="italic">Fifth</span> Lorem ipsum dolor sit amet...
		</Heading>
		<Loreum repetition={20} />
	</div>
</div>
