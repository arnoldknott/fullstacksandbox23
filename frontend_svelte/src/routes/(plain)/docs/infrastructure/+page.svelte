<script lang="ts">
	import RevealJs from '$components/RevealJS.svelte';
</script>

<RevealJs>
	<section>
		<h1>Azure Cloud</h1>
		<ul>
			<li><a href="#/infrastructure-as-code">Infrastructure as Code</a></li>
			<li><a href="#/resources">Resources</a></li>
			<li><a href="#/identity-management">Identity Management</a></li>
		</ul>
	</section>
	<section id="infrastructure-as-code">
		<h3>Infrastructure as Code</h3>
		<section>
			<ul>
				<li>Using OpenTofu as a Terraform clone</li>
				<li>Modules</li>
				<li>Variables</li>
				<li>State</li>
			</ul>
		</section>
		<section>
			<h3>Modules</h3>
			<ul>
				<li>Main</li>
				<li>App registrations</li>
				<li>Container apps</li>
				<li>Data</li>
				<li>Github Actions</li>
				<li>Security</li>
				<li>Vitual Machine</li>
				<li>Virtual Network</li>
			</ul>
		</section>
	</section>
	<section id="resources">
		<h3>Resources</h3>
		<section>
			<ul>
				<li>
					<em>Resource Groups</em> matching <em>dev, stage & prod</em> environments +
					<em>housekeeping</em>
				</li>
				<li>
					<em>Azure Container Apps</em> (based on Kubernetes) for
					<em>Backend, Frontend & Cache</em>/li>
				</li>
				<li><em>Postgres</em> as database</li>
				<li><em>Redis</em> container as cache</li>
				<li><em>Key Vault</em> for secrets</li>
				<li><em>Virtual Network</em> for security</li>
				<li><em>App Service Plan & Log Analytics</em> for logging</li>
				<li><em>Storage Account</em> for data and backups</li>
			</ul>
		</section>
	</section>
	<section id="identity-management">
		<h3>Identity Management</h3>
		<section>
			<ul>
				<li><em>App registrations</em> for <em>Frontend and Backend</em></li>
				<li><em>Managed Identities</em> for <em>CI/CD pieplines</em></li>
				<li>
					<em>OAuth2</em> for <em>Authentication</em> of users and <em>Authorization</em> in Backend
					and MS Graph
				</li>
				<li>
					<em>Role, Scopes & Groups</em> configures tokens for
					<em>Role Based Access Control (RBAC)</em>
				</li>
			</ul>
		</section>
	</section>
</RevealJs>
