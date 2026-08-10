<script lang="ts">
	let {
		extraClasses = '',
		overlayModifier = {}
	}: {
		extraClasses?: string;
		overlayModifier?: Record<string, string>;
	} = $props();
</script>

<button
	type="button"
	class="btn btn-square btn-sm btn-outline btn-primary {extraClasses}"
	aria-haspopup="dialog"
	aria-expanded="false"
	aria-controls="collapsible-mini-sidebar"
	aria-label="Toggle Sidebar"
	{...overlayModifier}
>
	<!-- data-overlay="#collapsible-mini-sidebar"
    data-overlay-options={ JSON.stringify({ "backdropClasses": "overlay-backdrop transition duration-300 fixed inset-0 bg-base-300/60 overflow-y-auto", "backdropParent": "#scrollspy" }) } -->
	<!-- <div id="collapsible-mini-sidebar-backdrop" data-overlay-backdrop-template="overlay-backdrop transition duration-300 fixed inset-0 bg-base-300/60 overflow-y-auto" style="z-index: 79;" class=""></div> -->
	<span
		class="icon-[material-symbols--menu-open-rounded] overlay-minified:hidden flex size-5 max-sm:hidden"
	></span>
	<span class="icon-[material-symbols--menu] overlay-minified:flex hidden size-5 max-sm:flex"
	></span>
</button>
