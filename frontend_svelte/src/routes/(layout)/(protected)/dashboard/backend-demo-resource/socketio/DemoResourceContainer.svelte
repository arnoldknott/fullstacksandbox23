<script lang="ts">
    import type { DemoResourceExtended } from '$lib/types';
    import { Action } from '$lib/accessHandler';
    let { demoResource, deleteResource = (_id: string) => {} } : { demoResource: DemoResourceExtended, deleteResource: (id: string) => void } = $props();
</script>

<div class="bg-base-300 shadow-shadow m-2 flex flex-col rounded-xl p-2 shadow-xl">
    <div class="flex flex-row justify-between">
        <h5 class="title justify-self-start">{demoResource.name}</h5>
        <div class="label justify-self-end">
            {demoResource.creation_date?.toLocaleString('da-DK', { timeZone: 'CET' })}
        </div>
    </div>
    <div class="flex flex-row">
        <div class="body-small grow">
            <p>{demoResource.description}</p>
        </div>
        {#if demoResource.user_right === Action.Write || demoResource.user_right === Action.Own}
            <div class="join flex flex-row items-end justify-center">
                <button
                    class="btn btn-secondary-container text-secondary-container-content btn-sm join-item grow"
                    aria-label="Edit Button"
                >
                    <!-- onclick={() => (edit ? (edit = false) : (edit = true))} -->
                    <span class="icon-[material-symbols--edit-outline-rounded]"></span>
                </button>
                {#if demoResource.user_right === Action.Own}
                    <div class="dropdown join-item relative inline-flex grow [--placement:top]">
                        <!-- bind:this={actionButtonShareMenuElement} -->
                        <button
                            id="action-share"
                            class="dropdown-toggle btn btn-secondary-container text-secondary-container-content btn-sm w-full rounded-none"
                            aria-haspopup="menu"
                            aria-expanded="false"
                            aria-label="Share with"
                        >
                            <span class="icon-[tabler--share-2]"></span>
                            <span class="icon-[tabler--chevron-up] dropdown-open:rotate-180 size-4"></span>
                        </button>
                    </div>
                    <button
                        class="btn btn-error-container bg-error-container/70 hover:bg-error-container/50 focus:bg-error-container/50 text-error-container-content btn-sm join-item grow border-0"
                        aria-label="Delete Button"
                        name="id"
                        onclick={() => !demoResource.id || deleteResource(demoResource.id)}
                    >
                        <span class="icon-[tabler--trash]"></span>
                    </button>
                {/if}
            </div>
        {/if}
    </div>
</div>