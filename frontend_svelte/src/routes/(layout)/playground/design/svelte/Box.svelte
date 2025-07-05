<script lang="ts">
import type { Snippet } from 'svelte';
    let { title, header, children }: { title: string, header?: Snippet; children: Snippet } = $props();
</script>

<div class="w-full">
    <div class="title-large text-center">{title}</div>

    <div class="bg-base-150 shadow-outline h-120 w-full rounded-lg p-2 shadow-inner">
        {#if header}
            {@render header()}
            <div class="divider divider-outline"></div>
        {/if}
        {@render children?.()}
    </div>
</div>