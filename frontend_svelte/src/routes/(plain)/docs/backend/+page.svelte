<section>
	<h1>Backend</h1>
	<ul>
		<li><a href="#/services">Services</a></li>
		<li><a href="#/design">Design</a></li>
		<li><a href="#/technologies">Technologies</a></li>
	</ul>
</section>
<section id="services">
	<h3>Services</h3>
	<section>
		<p>REST API</p>
		<ul>
			<li>POST, GET, PUT and DELETE operations</li>
			<li>Access Control</li>
			<li>Logging</li>
		</ul>
	</section>
	<section>
		<p>Socket.io server</p>
		<ul>
			<li>Realtime communication</li>
			<li>Namespaces synchronized with Resource hierarchy</li>
			<li>Rooms synchronized with Identity hierarchy</li>
			<li>Access Control</li>
		</ul>
	</section>
	<section>
		<p>Websockets</p>
		<ul>
			<li>Realtime communication</li>
			<li>Access Control</li>
			<li>Logging</li>
		</ul>
	</section>
</section>
<section id="design">
	<h3>Design</h3>
	<section>
		<p>View layer</p>
		<ul>
			<li>Configures endpoints and events</li>
			<li>Provides data integrity checks for incoming and outgoing data via external interfaces</li>
			<li>BaseView and BaseEvent class with pre-configured</li>
			<ul>
				<li>OAuth2 towards endpoints and events</li>
				<li>Interface to CRUD layer</li>
			</ul>
		</ul>
	</section>
	<section>
		<p>Create-Read-Update-Delete (CRUD) layer</p>
		<ul>
			<li>Interface to View Layer</li>
			<li>BaseCRUD provides pre-configured:</li>
			<ul>
				<li>uses fine based Access Control</li>
				<li>provides logging</li>
				<li>interacts with Postgres database</li>
			</ul>
		</ul>
	</section>
	<section>
		<p>Model layer</p>
		<ul>
			<li>models resources and identities</li>
			<li>provides data integrity checks towards database</li>
			<li>configures relations between resources</li>
			<li>configures relations between identities</li>
		</ul>
	</section>
	<section>
		<p>Unit Tests</p>
		<ul>
			<li>for all endpoints</li>
			<li>for security</li>
			<li>for hierarchies</li>
			<li>for Access Policies</li>
			<li>for Access logging</li>
		</ul>
	</section>
	<section>
		<p>Core</p>
		<ul>
			<li>Kayvault access</li>
			<li>Security functionality for Token verification</li>
			<li>Application configuration</li>
			<li>Logging configuration</li>
			<li>Type safety</li>
			<li>Database and Cache connections</li>
		</ul>
	</section>
	<section>
		<p>Database Migrations</p>
		<ul>
			<li>Checks migrations</li>
			<li>Creates migration scripts</li>
			<li>Keeps migration revisions</li>
			<li>Applies migrations</li>
		</ul>
	</section>
</section>
<section id="technologies">
	<h3>Technologies</h3>
	<section>
		<p>Python</p>
		<ul>
			<li>FastAPI - fully asynchronous design based on Starlette</li>
			<li>SQLModel - including</li>
			<ul>
				<li>Pydantic for data type checks and SQLAlchemy</li>
				<li>SQLAlchemy as Object Relational Manager for database interaction</li>
			</ul>
			<li>Websockets</li>
			<li>Socket.io server</li>
		</ul>
	</section>
</section>
