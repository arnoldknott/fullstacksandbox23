<script lang="ts">
	import RevealJs from '$components/RevealJS.svelte';
</script>

<RevealJs>
	<section>
		<h1>Architecture</h1>
		<ul>
			<li><a href="#/containers">Containers</a></li>
			<li><a href="#/storage">Storage</a></li>
			<li><a href="#/connections">Connections</a></li>
		</ul>
	</section>
	<section id="containers">
		<h3>Containers</h3>
		<section>
			<p>Docker images</p>
			<ul>
				<li><em>Backend</em> based on Python image with base, dev and prod stages</li>
				<li><em>Frontend</em> based Node image with build and prod stages</li>
				<li><em>Cache</em> Redis-stack image</li>
			</ul>
		</section>
		<section>
			<p>Docker compose</p>
			<ul>
				<li><em>dev</em> for development with <code>docker compose up</code></li>
				<li>
					<em>test</em> as a temporary environment running automated code formating, tests and
					linting before commit and in <em>Continuous Integration</em> pipeline
				</li>
				<li><em>prod</em> used both for staging and production environments</li>
			</ul>
		</section>
	</section>
	<section id="storage">
		<h3>Storage</h3>
		<section>
			<p>Postgres database</p>
			<ul>
				<li><em>Relational data storage</em></li>
				<li><em>Access Control</em> fine based</li>
				<li><em>Access Logging</em> detailed and reusable access data</li>
				<li>Containerized in <em>dev</em> and <em>test</em> environments</li>
				<li>Managed service in <em>stage</em> and <em>prod</em> environments</li>
			</ul>
		</section>
		<section>
			<p>Redis cache</p>
			<ul>
				<li><em>Session Management</em> in <em>Frontend</em></li>
				<li><em>Caching</em> of Tokens</li>
				<li>Containerized in <em>dev</em> and <em>test</em> environments</li>
			</ul>
		</section>
		<section>
			<p>Storage account</p>
			<ul>
				<li>provides volumes for redis and backend application data</li>
				<li>automated backup services</li>
			</ul>
		</section>
	</section>
	<section id="connections">
		<h3>Connections</h3>
		<section>
			<p>Backend</p>
			<ul>
				<li>REST API</li>
				<li>Socket.io server</li>
				<li>Websockets</li>
			</ul>
		</section>
		<section>
			<p>Open ports</p>
			<ul>
				<li>Backend to reach backend connections</li>
				<li>Frontend to serve frontend</li>
				<li>
					<em>Postgres</em> and <em>Redis</em> are not reachable from the outside in <em>prod</em>
				</li>
				<li><em>Postgres</em> can be reached in <em>staging</em> through PGAdmin tools</li>
			</ul>
		</section>
	</section>
</RevealJs>
