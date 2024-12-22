<script lang="ts">
    let { background, color } : { background: string, color: string} = $props();
    const text = background.replace('--md-sys-color-', '').replaceAll('-', ' ')
</script>

<div
    class="flex h-24 grow p-2"
    style="background-color: var({background});"
    >
    <p
        class="text-left text-base md:text-xl"
        style="color: var({color});"
    >
        {text}
    </p>
</div>