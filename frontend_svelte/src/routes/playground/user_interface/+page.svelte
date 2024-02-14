<script lang="ts">
    import { onMount } from 'svelte';
    import Title from '$components/Title.svelte';

    onMount(async () => {
    const te = await import('tw-elements');
    te.initTE(
        { MultiRangeSlider: te.MultiRangeSlider  },
        { allowReinits: true, checkOtherImports: true }
    );
    });

    $: sliderValue = 0;
    $: color = `hsl(${(sliderValue) * 1.2}, 80%, 80%)`;
</script>

<!-- <div class="px-10">
    <label
        for="customRange1"
        class="mb-2 inline-block text-primary-700 dark:text-primary-300"
        >Status</label
    >
    <input
        type="range"
        data-te-tooltip="true"
        class="transparent h-[4px] w-full cursor-pointer appearance-none border-transparent bg-neutral-200 dark:bg-neutral-600"
        id="customRange1" />
</div> -->

<Title>Status slider</Title>

<div data-te-multi-range-slider-init
    data-te-tooltip="true"
    data-te-number-of-ranges="1"
    on:valueChanged.te.multiRangeSlider={e => sliderValue = e.values.rounded}
    class=p-10>
    { sliderValue }
</div>

<div class="w-100 m-10 p-10" style="background-color: {color};">
    STATUS: {sliderValue}
</div>