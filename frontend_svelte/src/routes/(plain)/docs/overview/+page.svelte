<script lang="ts">
    import { SocketIO } from "$lib/socketio";
    import "@material/web/textfield/filled-text-field.js";
    import "@material/web/button/elevated-button.js";
    import '@material/web/slider/slider.js';
    import '@material/web/chips/chip-set.js';
    import '@material/web/chips/assist-chip.js';
    // import '@material/web/chips/input-chip.js';
    // import '@material/web/chips/filter-chip.js';
    // import '@material/web/chips/suggestion-chip.js';


    import type { SocketioConnection } from "$lib/types";

    // let { keyboard = $bindable(false) }: { keyboard: boolean } = $props();
    // let keyboard = false

    const connection: SocketioConnection = {
        event: "demo_message",
        namespace: "",
        room: ""
    };

    const socketio = new SocketIO(connection);
    let newMessage = $state("");

    let replies: string[] = $state([]);

    let topics = $state([
        { name: "Repository", value: 50, comment: "" },
        { name: "Infrastructure", value: 50, comment: "" },
        { name: "Architecture", value: 50, comment: "" },
        { name: "Security", value: 50, comment: "" },
        { name: "Backend", value: 50, comment: "" },
        { name: "Frontend", value: 50, comment: "" }
    ])

    let colors = $derived.by(() => topics.map((topic) => `hsl(${topic.value * 1.2}, 80%, 80%)`))

    // let colors = $derived.by( () => topics.forEach( (topic) => `hsl(${topic.value * 1.2}, 80%, 80%)`))

    // TBD: add as method to SocketIO class
    const sendMessage = (event: Event) => {
        event.preventDefault();
        const target = event.target as HTMLElement | null;
        const name = target ? target.id : "";
        const topic = topics.find(t => t.name === name);
        const message = topic ? topic.comment.trim() : "";
        const namespace = name.toLowerCase();
        console.log(`Sending message in namespace ${namespace}`, message);
        socketio.client.emit(connection.event, message);
        if (topic) {
            topic.comment = "";
        }
    };

    $effect(() => {
        socketio.client.on(connection.event, (data) => {
            replies.push(`${data}`);
        });
    });
</script>


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
	<h3>Backend</h3>
	<ul>
		<li>Services</li>
		<li>Design</li>
		<li>Technologies</li>
	</ul>
</section>
<section id="frontend">
	<h3>Frontend</h3>
	<ul>
		<li>Services</li>
		<li>Design</li>
		<li>Technologies</li>
	</ul>
</section>
<section id="inputs" class="w-screen">
    <p>Select your interest in this topic and comment on it</p>
    <div class="grid grid-cols-2 gap-8">
        <div class="h-[700px] overflow-y-scroll">
            {#each topics as topic, i}
                <div class="flex flex-col my-2" style="background-color: {colors[i]};">
                    <form id={topic.name}  method="POST" onsubmit={sendMessage}>
                        <div class="flex flex-row justify-left" >
                            <div class="w-full flex  flex-row">
                                <span class="text-black justify-left">{topic.name}:</span>
                                <div class="w-full justify-end">
                                    <span class="text-black text-xl">👎</span>
                                    <md-slider
                                        class="w-3/5"
                                        min="0"
                                        max="100"
                                        step="1"
                                        value={topic.value}
                                        oninput={(e: Event) => (topic.value = parseInt((e.target as HTMLInputElement).value))}
                                    >
                                    </md-slider>
                                    <span class="text-black text-xl">👍</span>
                                </div>
                            </div>
                        </div>
                        <div class="p-2 flex flex-row">
                            <md-filled-text-field
                                label="Comments"
                                type="input"
                                name="message"
                                value={topic.comment}
                                oninput={(e: Event) => (topic.comment = (e.target as HTMLInputElement).value)}
                                class="w-full mr-2"
                            >
                            </md-filled-text-field>
                            <div>
                                    <md-elevated-button type="submit" role="button"  tabindex="0" class="my-1">
                                        Send
                                    </md-elevated-button>
                            </div>
                        </div>
                    </form>
                </div>
            {/each}
        </div>
        <div >
            <span>Results - cahnge to averaged!</span>
            <md-chip-set>
                {#each topics as topic, i}
                    <md-assist-chip label={topic.name} style="background-color: {colors[i]};"></md-assist-chip>    
                {/each}
            </md-chip-set>
            <div class="h-[700px] overflow-y-scroll">
                <p>Replies</p>
                {#each replies as reply}
                    <span class=" text-3xl">{reply}</span><br />
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