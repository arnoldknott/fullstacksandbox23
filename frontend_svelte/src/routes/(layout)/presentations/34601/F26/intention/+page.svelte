<script lang="ts">
	import RevealJS from '$components/RevealJS.svelte';
	import MotivationTable from './MotivationTable.svelte';
	import SlideTitle from './SlideTitle.svelte';
</script>

<RevealJS>
	<section>
		<div class="relative h-full p-10">
			<div class="absolute top-2 right-10">Some absolut text</div>
			<SlideTitle>Sharing Round</SlideTitle>
			<div class="chat chat-receiver">
				<div class="chat-bubble chat-bubble-accent">One Answer!</div>
			</div>
			<div class="chat chat-sender">
				<div class="chat-bubble">
					Another answer - might be a reaction to the first or a stand alone! What happens if this
					answer exceeds a certain length? Will it wrap around correctly and still be readable?
				</div>
			</div>
		</div>
	</section>
	<section>
		<SlideTitle>Motivation</SlideTitle>
		<p>Self determination theory:</p>
		<p class="text-error">Consider removing?</p>
		<ul>
			<li>Autonomy</li>
			<li>Competence</li>
			<li>Sense of Belonging</li>
			<li>(Meaning)</li>
		</ul>
	</section>
	<section>
		<section>
			<SlideTitle>Motivation</SlideTitle>
			<MotivationTable />
		</section>
	</section>
	<section>
		<SlideTitle>Inclusion</SlideTitle>
	</section>
	<section>
		<SlideTitle>My motivation</SlideTitle>
		<p class="text-error">Consider removing?</p>
	</section>
	<section>
		<SlideTitle>To pass the course...</SlideTitle>
	</section>
</RevealJS>
