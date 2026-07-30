<script lang="ts">
	import { page } from '$app/state';
	import Display from '$components/Display.svelte';
	import Heading from '$components/Heading.svelte';
</script>

<Display id="presentation">Presentation</Display>
<Heading id="presentation-title">{page.params.id}</Heading>

<div
	class="title-large alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
	role="alert"
>
	Source
	<p class="title text-center">
		A card to set the source of the code for the presentation, like "intern", "github", which
		branch, and or commit, and so on
	</p>
</div>
<div
	class="title-large alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
	role="alert"
>
	Access
	<p class="title text-center">
		Setting the access for the presentation, like "public", "private", "shared with specific users
		or groups", that is access policies.
	</p>
</div>
<div
	class="title-large alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
	role="alert"
>
	Questions
	<p class="title text-center">
		Linked questions. Adding a question and opening sidebar to select existing questions - for mode
		copy (don't keep the original answers and don't keep in sync) or link (keeps answers in sync)
	</p>
</div>
<div
	class="title-large alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
	role="alert"
>
	Links
	<p class="title text-center">
		Links, that are under continuous check for 200 responses that are used inside the presentation.
	</p>
</div>
<div
	class="title-large alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
	role="alert"
>
	(Drawings)
	<p class="title text-center">
		Draw.io and Excalibur, that are linked and used inside the presentation. Add anew, modify linked
		or iopen sidedrawer for linking / copying existing. Maybe work with templates?
	</p>
</div>
<div
	class="title-large alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
	role="alert"
>
	Files
	<p class="title text-center">
		Uploading, updating, deleting files, that are referenced in the presentation. Can also open a
		side drawer for managing existing files.
	</p>
</div>
<div
	class="title-large alert alert-warning bg-warning-container/20 text-warning-container-content/80 label-large text-center"
	role="alert"
>
	(Maybe languages?, AI activation?, ...)
</div>
