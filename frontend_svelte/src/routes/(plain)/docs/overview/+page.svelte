<script lang="ts">
	import RevealJs from '$components/RevealJS.svelte';
	import { SocketIO } from '$lib/socketio';

	import type { SocketioConnection } from '$lib/types';

	// let { keyboard = $bindable(false) }: { keyboard: boolean } = $props();
	// let keyboard = false

	const connection: SocketioConnection = {
		event: 'comments', // does not really matter here, I guess?
		// namespace: '/presentation_interests',
		namespace: '/interactive-documentation',
		room: 'does_not_matter_here_either'
	};

	const socketio = new SocketIO(connection);

	type Reply = {
		name: string;
		comment: string;
	};
	let replies: Reply[] = $state([]);

	type Topic = {
		name: string;
		value: number;
		comment: string;
		average: number;
		count: number;
	};

	let topics: Topic[] = $state([
		{ name: 'Repository', value: 50, comment: '', average: 50, count: 0 },
		{ name: 'Infrastructure', value: 50, comment: '', average: 50, count: 0 },
		{ name: 'Architecture', value: 50, comment: '', average: 50, count: 0 },
		{ name: 'Security', value: 50, comment: '', average: 50, count: 0 },
		{ name: 'Backend', value: 50, comment: '', average: 50, count: 0 },
		{ name: 'Frontend', value: 50, comment: '', average: 50, count: 0 }
	]);

	let input_colors = $derived.by(() =>
		topics.map((topic) => `hsl(${topic.value * 1.2}, 80%, 80%)`)
	);
	let average_colors = $derived.by(() =>
		topics.map((topic) => `hsl(${topic.average * 1.2}, 80%, 80%)`)
	);

	// TBD: add as method to SocketIO class
	const submitForm = async (event: Event) => {
		console.log('sendMessage triggered');
		event.preventDefault();
		const target = event.target as HTMLElement | null;
		const name = target ? target.id : '';
		const topic = topics.find((t) => t.name === name);
		if (topic) {
			await sendMessage(topic);
		}
	};

	const sendMessage = async (topic: Topic) => {
		const name = topic.name;
		const message = topic ? topic.comment.trim() : '';
		const value = topic ? topic.value : 50;
		socketio.client.emit('comments', { topic: name, comment: message, value: value });
		if (topic) {
			topic.comment = '';
		}
	};

	$effect(() => {
		socketio.client.on('server_comments', (data) => {
			console.log(`Received from socket.io server: ${data}`);
			if (data.comment !== '') {
				replies.push({ name: data.topic, comment: data.comment });
			}
		});
		socketio.client.on('averages', (data) => {
			console.log(`Average for ${data.topic}: ${data.average}`);

			const topic = topics.find((t) => t.name === data.topic);
			if (topic) {
				topic.average = data.average;
				topic.count = data.count;
			}
		});
	});
</script>

<RevealJs keyboard={false}>
	<section>
		<h1>Fullstack Sandbox23</h1>
		<ul>
			<li><a href="#/repository">Repository</a></li>
			<li><a href="#/infrastructure">Infrastructure</a></li>
			<li><a href="#/architecture">Architecture</a></li>
			<li><a href="#/security">Security</a></li>
			<li><a href="#/backend">Backend</a></li>
			<li><a href="#/frontend">Frontend</a></li>
		</ul>
	</section>
	<section id="repository">
		<h3>Repository: Github</h3>
		<ul>
			<li>Code Base</li>
			<li>Continuous Integration / Continuous Deployment</li>
			<li>Container Registry</li>
			<li>Environments</li>
		</ul>
	</section>
	<section id="infrastructure">
		<h3>Infrastructure: Azure Cloud</h3>
		<ul>
			<li>Infrastructure as Code</li>
			<li>Resources</li>
			<li>Identity Management</li>
		</ul>
	</section>
	<section id="architecture">
		<h3>Architecture</h3>
		<ul>
			<li>Containers</li>
			<li>Storage</li>
			<li>Connections</li>
		</ul>
	</section>
	<section id="security">
		<h3>Security</h3>
		<ul>
			<li>Network</li>
			<li>OAuth2</li>
			<li>AccessControl</li>
			<li>Hierarchies</li>
			<li>Logging</li>
		</ul>
	</section>
	<section id="backend">
		<h3>Backend: FastAPI</h3>
		<ul>
			<li>Services</li>
			<ul>
				<li>REST API</li>
				<li>Socket.io</li>
				<li>Websockets</li>
				<li>Authorization</li>
				<li>Access Control</li>
				<li>Logging</li>
			</ul>
			<li>Design</li>
			<ul>
				<li>Models</li>
				<li>Views</li>
				<li>Controllers</li>
			</ul>
			<li>Technologies</li>
		</ul>
	</section>
	<section id="frontend">
		<h3>Frontend: Svelte5</h3>
		<ul>
			<li>Services</li>
			<ul>
				<li>Authentication</li>
				<li>Session Management</li>
			</ul>
			<li>Design</li>
			<li>Technologies</li>
			<ul>
				<li>Material Design</li>
				<li>TailwindCSS</li>
				<li>Reveal.JS</li>
			</ul>
		</ul>
	</section>
	<section id="inputs" class="w-screen">
		<p>Select your interest in this topic and comment on it</p>
		<div class="grid grid-cols-2 gap-8">
			<div class="h-[700px] overflow-y-scroll">
				{#each topics as topic, i (i)}
					<div class="my-2 flex flex-col" style="background-color: {input_colors[i]};">
						<form id={topic.name} method="POST" onsubmit={submitForm}>
							<div class="justify-left flex flex-row">
								<div class="flex w-full flex-row">
									<span class="justify-left p-2 text-2xl text-black/70">{topic.name}:</span>
									<div class="w-full justify-end">
										<span class="text-xl text-black">👎</span>
										<input
											type="range"
											class="range range-secondary bg-base-content w-4/5"
											min="0"
											max="100"
											step="1"
											value={topic.value}
											oninput={(e: Event) =>
												(topic.value = parseInt((e.target as HTMLInputElement).value))}
										/>
										<span class="text-xl text-black">👍</span>
									</div>
								</div>
							</div>
							<div class="flex flex-row gap-2">
								<div class="input-filled input-neutral w-full grow">
									<input
										id={topic.name}
										type="text"
										class="input border-neutral text-neutral"
										placeholder=""
										name="message"
										tabindex="0"
										value={topic.comment}
										oninput={(e: Event) => (topic.comment = (e.target as HTMLInputElement).value)}
										onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && sendMessage(topic)}
									/>
									<label class="input-filled-label text-neutral" for="filledInputSecondary">Comments</label
									>
								</div>
								<div>
									<button class="btn btn-secondary rounded-full" type="submit" tabindex="0">
										Send
									</button>
								</div>
							</div>
						</form>
					</div>
				{/each}
			</div>
			<div>
				<div>Results</div>
				<div class="flex flex-row w-full gap-2">
					{#each topics as topic, i (i)}
						<div
							class="badge badge-xl text-label grow"
							style="background-color: {average_colors[i]};"
						>
							{topic.name}: {topic.count}
						</div>
					{/each}
				</div>
				<div class="h-[650px] overflow-y-scroll w-full">
					<p>Replies</p>
					<ul class="divide-base-content/25 w-full *:p-3" style="list-style-type: none;">
						{#each replies as reply, i (i)}
							<li class="w-full">
								<div
									style="color: {average_colors[topics.findIndex((t) => t.name === reply.name)]}"
									class="text-left text-2xl font-bold"
								>
									{reply.name}
								</div>
								<div class="text-left text-xl text-white">
									{reply.comment}
								</div>
								<div class="divider divider-outline after:border-t-4 before:border-t-4"></div>
							</li>
						{/each}
					</ul>
				</div>
			</div>
		</div>
	</section>

</RevealJs>

<style>
	ul { 
		list-style-type: dot; 
	}
</style>