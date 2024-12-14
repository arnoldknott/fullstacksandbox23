<script lang="ts">
	import '@material/web/labs/card/filled-card.js'; // refactor into parent element Card.svelte
	import '@material/web/tabs/tabs.js';
	import '@material/web/tabs/primary-tab.js';
	import '@material/web/tabs/secondary-tab.js';
	import '@material/web/list/list.js';
	import type { Tab } from '$lib/types';
	import type { Snippet } from 'svelte';

	let { tabs, children }: { tabs: Tab[]; children: Snippet } = $props();

	let activeTab = $state(tabs.findIndex((tab) => tab.active == true) || 0);
	const tabChange = (event: Event) => (activeTab = event.target ? event.target.activeTabIndex : 0);
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
		<md-list>
			<md-list-item>{@render children?.()}</md-list-item>
			<!-- <Chat {connection}>{tabs[activeTab].content}</Chat> -->
		</md-list>
		<p>{tabs[activeTab].content} in Tabs</p>
	</div>
</md-filled-card>

<!-- TBD: use inside Cards -->

<style>
	md-filled-card {
		width: 90%;
		padding: 10px;
		margin: 20px;
		text-align: center;
		--md-filled-card-container-color: var(--md-sys-color-primary);
		/* works: */
		/* --md-filled-card-container-color: #ffcc00; */
	}
</style>
