<section>
	<h1>Github</h1>
	<ul>
		<li><a href="#/code-base">Code Base</a></li>
		<li><a href="#/ci-cd">Continuous Integration / Continuous Deployment</a></li>
		<li><a href="#/container-registry">Container Registry</a></li>
		<li><a href="#/environments">Environments</a></li>
	</ul>
</section>
<section id="code-base">
	<h3>Code Base</h3>
	<section>
		<ul>
			<li>
				Branches to match environments
				<ul>
					<li><em>dev ⇒ dev</em> for development</li>
					<li><em>stage ⇒ stage</em> for staging / pre-production</li>
					<li><em>main ⇒ prod</em> for production</li>
				</ul>
			</li>
		</ul>
	</section>
	<section>
		<ul>
			<li>
				Pull requests
				<ul>
					<li><em>dev ⇒ stage ⇒ main</em></li>
					<li>Trigger pipelines</li>
				</ul>
			</li>
		</ul>
	</section>
</section>
<section id="ci-cd">
	<h3>Continuous Integration / Continuous Deployment</h3>
	<section>
		<ul>
			<li>
				Pipelines
				<ul>
					<li>Infrastructure</li>
					<li>Backend</li>
					<li>Frontend</li>
				</ul>
			</li>
		</ul>
	</section>
	<section>
		<ul>
			<li>
				Infrastructure jobs
				<ul>
					<li>using OpenTofu (Terraform clone)</li>
					<li><em>plan</em></li>
					<li><em>apply</em></li>
				</ul>
			</li>
		</ul>
	</section>
	<section>
		<ul>
			<li>
				Backend jobs
				<ul>
					<li><em>test</em> for code formating, linting and testing</li>
					<li>
						<em>check for infrastructure changes</em> prevents deployment until infrastructure is successfully
						deployed
					</li>
					<li>
						<em>containerize</em> builds the production container and pushes it to github container repository
					</li>
					<li>
						<em>deploy to stage</em> automatically deploys to staging environment in
						<em>stage & main</em> branches
					</li>
					<li><em>check migrations</em> for database state</li>
					<li><em>create migration scripts</em> for automated migrations</li>
					<li>
						<em>deploy to prod</em> manually deploys to production environment in <em>main</em> branch
					</li>
				</ul>
			</li>
		</ul>
	</section>
	<section>
		<ul>
			<li>
				Frontend jobs
				<ul>
					<li><em>test</em> for code formating, linting and testing</li>
					<li>
						<em>check for infrastructure changes</em> prevents deployment until infrastructure is successfully
						deployed
					</li>
					<li>
						<em>containerize</em> builds the production container and pushes it to github container repository
					</li>
					<li>
						<em>deploy to stage</em> automatically deploys to staging environment in
						<em>stage & main</em> branches
					</li>
					<li>
						<em>deploy to prod</em> manually deploys to production environment in <em>main</em> branch
					</li>
				</ul>
			</li>
		</ul>
	</section>
</section>
<section id="container-registry">
	<h3>Container Registry</h3>
	<p>Images</p>
	<ul>
		<li>Frontend</li>
		<li>Backend</li>
	</ul>
</section>
<section id="environments">
	<h3>Environments</h3>
	<ul>
		<li>keep secrets</li>
		<li>keep environment variables</li>
		<li>define manual approval steps</li>
	</ul>
</section>
