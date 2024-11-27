<script lang="ts">
	import RevealJs from '$components/RevealJS.svelte';
</script>

<RevealJs>
	<section>
		<h1>Security</h1>
		<ul>
			<li><a href="#/network">Network</a></li>
			<li><a href="#/oauth2">OAuth2</a></li>
			<li><a href="#/access-control">Access Control</a></li>
			<li><a href="#/hierarchies">Hierarchies</a></li>
			<li><a href="#/logging">Logging</a></li>
		</ul>
	</section>
	<section>
		<h3>Network</h3>
		<section>
			<p>Security measures</p>
			<ul>
				<li>
					<em>Kubernetes</em> closes access to data and only opens ports for <em>Backend</em> and
					<em>Frontend</em>
				</li>
				<li><em>HTTPS</em> for secure communication</li>
				<li><em>OAuth2</em> for authentication and authorization</li>
				<li><em>Access Control</em> for fine grained access permissions</li>
				<li><em>Logging</em> for tracking access</li>
			</ul>
		</section>
	</section>
	<section id="oauth2">
		<h3>OAuth2</h3>
		<section>
			<p>Authentication and Protection of endpoints in view layer</p>
			<ul>
				<li><em>Authentication</em> based with Azure Entra AD as identity service provider</li>
				<li><em>Authorization Code flow with PKCE</em></li>
				<li><em>Authorization</em> tokens are configured with Roles, Scopes and Groups:</li>
				<ul>
					<li><em>Roles</em> as User and Admin</li>
					<li>
						<em>Scopes</em> for distinguishing between API, Socket.IO, and Artificial Intelligence parts
						of application and read and write access
					</li>
					<li>
						<em>Groups</em> for fine grained access control - can be linked to Office365 groups
					</li>
				</ul>
			</ul>
		</section>
	</section>
	<section id="access-control">
		<h3>Fine grained Access Control for Access Permissions on resource level</h3>
		<section>
			<p>Actions</p>
			<ul>
				<li><em>Own</em> can read, write and add new permissions for others (share)</li>
				<li><em>Write</em> can read and write resources</li>
				<li><em>Read</em> can read resources</li>
			</ul>
		</section>
	</section>
	<section id="hierarchies">
		<h3>Hierarchies</h3>
		<section>
			<ul>
				<li>Two hierarchies:</li>
				<ul>
					<li><em>Identities</em> for users, groups of users, and groups of groups, ...</li>
					<li><em>Resources</em> for resources, groups of resources, and groups of groups, ...</li>
				</ul>
				<li>Permissions consist of <em>Action</em>, <em>Identity</em> and <em>Resource</em></li>
				<li>Override flags:</li>
				<ul>
					<li><em>Public</em> anybody (after potential OAuth2 guards) can access</li>
					<li>
						<em>Inherit</em> can be true or false to prevent inheritance from parent resources
					</li>
				</ul>
			</ul>
		</section>
	</section>
	<section id="logging">
		<h3>Logging</h3>
		<section>
			<ul>
				<li>
					<em>Requests</em> are compared to permissions table and all requests are logged, including:
				</li>
				<ul>
					<li>User</li>
					<li>Resource</li>
					<li>Action</li>
					<li>Result</li>
					<li>Timestamp</li>
				</ul>
			</ul>
		</section>
	</section>
</RevealJs>
