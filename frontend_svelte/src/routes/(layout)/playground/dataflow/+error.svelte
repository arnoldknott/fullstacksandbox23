<script lang="ts">
	import { goto } from "$app/navigation";

    const redirect = () => {
        goto("/playground/dataflow");
    }
</script>

<div class="text-center">
    <div class="heading text-error">⚡️ Error page ⚡️</div>
    <p class="p-4">Go back to <button class="btn ml-10" onclick={redirect}>data flow</button></p>
</div>