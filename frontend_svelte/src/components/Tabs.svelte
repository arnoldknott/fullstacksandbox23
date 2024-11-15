<script lang="ts">
	import '@material/web/labs/card/filled-card.js'; // refactor into parent element Card.svelte
	import '@material/web/tabs/tabs.js';
	import '@material/web/tabs/primary-tab.js';
	import '@material/web/tabs/secondary-tab.js';
	import '@material/web/list/list.js';
	import Title from '$components/Title.svelte';

	let { tabs, children } = $props();

	console.log('=== lib - components - tabs - tabs ===');
	console.log(tabs);

	let activeTab = $state(tabs.findIndex((tab) => tab.active == true) || 0);
	const tabChange = (event: Event) => (activeTab = event.target.activeTabIndex);
</script>

<md-filled-card class="w-80 py-10">
	<md-tabs onchange={tabChange}>
		{#each tabs as tab, i}
			<md-primary-tab active={activeTab == i}>
				{tab.header}
			</md-primary-tab>
		{/each}
	</md-tabs>
	<div class="p-10">
		<Title>{tabs[activeTab].content}</Title>
		<md-list>
			<md-list-item>{@render children?.()}</md-list-item>
		</md-list>
	</div>
</md-filled-card>

<!-- TBD: use inside Cards -->

<style>
	md-filled-card {
		width: 80%;
		padding: 10px;
		margin: 20px;
		text-align: center;
		--md-filled-card-container-color: var(--md-sys-color-primary);
		/* --md-filled-card-container-color: #ffcc00; works */
	}
</style>
