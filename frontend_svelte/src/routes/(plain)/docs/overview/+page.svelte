<script lang="ts">
	import RevealJs from '$components/RevealJS.svelte';
	import { SocketIO } from '$lib/socketio';
	import '@material/web/textfield/filled-text-field.js';
	import '@material/web/button/elevated-button.js';
	import '@material/web/slider/slider.js';
	import '@material/web/chips/chip-set.js';
	import '@material/web/chips/assist-chip.js';
	import '@material/web/list/list.js';
	import '@material/web/list/list-item.js';
	import '@material/web/divider/divider.js';
	// import '@material/web/chips/input-chip.js';
	// import '@material/web/chips/filter-chip.js';
	// import '@material/web/chips/suggestion-chip.js';

	import type { SocketioConnection } from '$lib/types';

	// let { keyboard = $bindable(false) }: { keyboard: boolean } = $props();
	// let keyboard = false

	const connection: SocketioConnection = {
		event: 'comments',// does not really matter here, I guess?
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
				{#each topics as topic, i}
					<div class="my-2 flex flex-col" style="background-color: {input_colors[i]};">
						<form id={topic.name} method="POST" onsubmit={submitForm}>
							<div class="justify-left flex flex-row">
								<div class="flex w-full flex-row">
									<span class="justify-left p-4 text-3xl text-black">{topic.name}:</span>
									<div class="w-full justify-end">
										<span class="text-xl text-black">👎</span>
										<md-slider
											class="w-4/5"
											min="0"
											max="100"
											step="1"
											value={topic.value}
											oninput={(e: Event) =>
												(topic.value = parseInt((e.target as HTMLInputElement).value))}
										>
										</md-slider>
										<span class="text-xl text-black">👍</span>
									</div>
								</div>
							</div>
							<div class="flex flex-row p-2">
								<md-filled-text-field
									label="Comments"
									type="input"
									name="message"
									role="textbox"
									tabindex="0"
									value={topic.comment}
									oninput={(e: Event) => (topic.comment = (e.target as HTMLInputElement).value)}
									onkeydown={(e: KeyboardEvent) => e.key === 'Enter' && sendMessage(topic)}
									class="mr-2 w-full"
								>
								</md-filled-text-field>
								<div>
									<md-elevated-button type="submit" role="button" tabindex="0" class="my-1">
										Send
									</md-elevated-button>
								</div>
							</div>
						</form>
					</div>
				{/each}
			</div>
			<div>
				<span>Results</span>
				<md-chip-set>
					{#each topics as topic, i}
						<md-assist-chip
							label={`${topic.name}: ${topic.count}`}
							style="background-color: {average_colors[i]};"
						></md-assist-chip>
					{/each}
				</md-chip-set>
				<div class="h-[650px] overflow-y-scroll">
					<p>Replies</p>
					{#each replies as reply}
						<md-list class="bg-transparent">
							<md-list-item>
								<div
									slot="headline"
									style="color: {average_colors[topics.findIndex((t) => t.name === reply.name)]}"
									class="text-left text-2xl font-bold"
								>
									{reply.name}
								</div>
								<div slot="supporting-text" class="text-left text-xl text-white">
									{reply.comment}
								</div>
								<md-divider></md-divider>
							</md-list-item>
						</md-list>
						<!-- <span class=" text-3xl">{reply}</span><br /> -->
					{/each}
				</div>
			</div>
		</div>
	</section>

	<style>
		md-filled-text-field {
			--md-filled-text-field-container-color: #ffbe6e;
		}
		md-elevated-button {
			--md-elevated-button-container-color: #ffbe6e;
		}
	</style>
</RevealJs>
