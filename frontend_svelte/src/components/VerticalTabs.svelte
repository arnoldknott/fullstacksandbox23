<script lang="ts">
	import { fly } from 'svelte/transition';

	let selectedIndex = 0;
	// const changeSecondTab = () => {
	// 	selectedIndex = 1;
	// };
	const changeTab = (index: number) => {
		selectedIndex = index;
	};
</script>

<div class="vertical-tab-container">
	<ul class="vertical-tab">
		<!-- <li class:selected={selectedIndex === 0}
            on:click={() => changeTab(0)}>First Tab</li> -->
		<!-- <li>Second Tab</li> -->
		<!-- <li on:click={() => changeSecondTab()}>Second Tab</li> -->
		<!-- <li class:selected={selectedIndex === 1}
            on:click={() => changeTab(1)}>Second Tab</li>
		<li class:selected={selectedIndex === 2}
            on:click={() => changeTab(2)}>Third Tab</li> -->
		<li>
			<button class:selected={selectedIndex === 0} on:click={() => changeTab(0)}>
				First Tab
			</button>
		</li>
		<li>
			<button class:selected={selectedIndex === 1} on:click={() => changeTab(1)}>
				Second Tab
			</button>
		</li>
		<li>
			<button class:selected={selectedIndex === 2} on:click={() => changeTab(2)}>
				Third Tab
			</button>
		</li>
	</ul>

	<div class="vertical-tab-content">
		<!-- <h2>First Tab Heading</h2>
		<p>
			Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem aut deserunt veniam tempora
			deleniti quos reprehenderit natus. Animi, obcaecati dolorum, culpa, maiores maxime ullam
			soluta unde rerum nihil temporibus quibusdam!
		</p> -->
		<!-- {#if selectedIndex == 0}
			<h2>First Tab Heading</h2>
			<p>
				Lorem ipsum dolor sit amet consectetur adipisicing elit. Autem aut deserunt veniam tempora
				deleniti quos reprehenderit natus. Animi, obcaecati dolorum, culpa, maiores maxime ullam
				soluta unde rerum nihil temporibus quibusdam!
			</p>
		{:else if selectedIndex == 1}
			<h2>Second Tab Heading</h2>
			<p>...</p>
		{/if} -->
		{#if selectedIndex == 0}
			<div transition:fly>
				<h2>First Tab Heading</h2>
				<p>First text ...</p>
			</div>
		{:else if selectedIndex == 1}
			<div transition:fly>
				<h2>Second Tab Heading</h2>
				<p>Second text ...</p>
			</div>
		{:else if selectedIndex == 2}
			<div transition:fly>
				<h2>Third Tab Heading</h2>
				<p>Third text ...</p>
			</div>
		{/if}
	</div>
</div>

<style>
	.vertical-tab-container {
		display: flex;
		flex-direction: row;
		align-items: center;
		border: 1px solid gray;
		border-radius: 1rem;
	}

	.vertical-tab {
		margin: 0px;
		padding: 3rem;
		list-style: none;
		border-right: 1px solid gray;
	}

	.vertical-tab li {
		margin: 2rem 0;
	}

	.vertical-tab-content {
		flex: 1;
		align-items: center;
	}

	.selected {
		color: blue;
	}
</style>
