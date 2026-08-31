<script lang="ts">
	import Person from './Person.svelte';
</script>

<div class="pointer-events-none absolute inset-0 mt-[100px]">
	<div class="relative h-full w-full">
		<div
			class="border-border color-secondary absolute inset-x-[10%] top-[12%] bottom-[12%] flex items-center justify-center rounded-[50%] border-8 bg-transparent text-9xl font-bold"
		>
			Team
		</div>
		<!-- <div class="pointer-events-auto absolute top-[5%] left-[30%] w-180">
			<NodeOverlay
				buttonExtraClasses="btn-secondary rounded-[50%]  h-50"
				cardExtraClasses="bg-secondary-container text-secondary-container-content right-[60%] text-4xl"
			>
				{#snippet buttonText()}
					Ahmed
				{/snippet}
				{#snippet header()}
					<Title id="ahmed">Ahmed Ammar</Title>
				{/snippet}
				<div class="flex flex-row gap-4">
					<img
						src="https://orbit.dtu.dk/files-asset/399014803/125707_2c599d15.jpg?w=160&f=webp"
						alt="Ahmed Ammar"
						class="h-auto w-40 mask-y-from-85% mask-y-to-100% mask-x-from-75% mask-x-to-100% object-contain opacity-70"
					/>

					<dl class="p-4">
						<dt>Module</dt>
						<dd class="mb-5">Printed Circuit Boards</dd>
						<dt><a href="https://orbit.dtu.dk/en/persons/ahmed-ammar/">Contact</a></dt>
					</dl>
				</div>
			</NodeOverlay>
		</div> -->
		<Person
			placement="top-[3%] left-[32%]"
			name="Ahmed"
			cardHeader="Ahmed Ammar"
			cardPlacement="right-[10%]"
			pictureLink={new URL(
				'https://orbit.dtu.dk/files-asset/399014803/125707_2c599d15.jpg?w=160&f=webp'
			)}
		>
			<dl class="p-4">
				<dt>Module</dt>
				<dd class="mb-5">Printed Circuit Boards</dd>
				<dt>
					<a class="link link-animated" href="https://orbit.dtu.dk/en/persons/ahmed-ammar/"
						>Contact</a
					>
				</dt>
			</dl>
		</Person>
		<Person
			placement="top-[7%] right-[55%]"
			name="Arnold"
			cardHeader="Arnold Knott"
			cardPlacement="left-[60%]"
			pictureLink={new URL(
				'https://orbit.dtu.dk/files-asset/421033490/37925_fa310472.jpg?w=160&f=webp'
			)}
		>
			<dl class="p-4">
				<dt class="mb-5">Course responsible</dt>
				<dt>Module</dt>
				<dd class="mb-5">Electromagentic Compatibility</dd>
				<dt>
					<a class="link link-animated" href="https://orbit.dtu.dk/en/persons/arnold-knott/"
						>Contact</a
					>
				</dt>
			</dl>
		</Person>
		<Person
			placement="top-[40%] right-[75%]"
			name="Gabriel"
			cardHeader="Tiberiu-Gabriel Zsurzsan"
			cardPlacement="left-[60%] "
			pictureLink={new URL(
				'https://orbit.dtu.dk/files-asset/449238439/62516_1c2df3b4.jpg?w=160&f=webp'
			)}
		>
			<dl class="p-4">
				<dt class="mb-5">Course responsible</dt>
				<dt>Module</dt>
				<dd class="mb-5">Printed Circuit Boards</dd>
				<dt>
					<a class="link link-animated" href="https://orbit.dtu.dk/en/persons/gabriel-zsurzsan/"
						>Contact</a
					>
				</dt>
			</dl>
		</Person>

		<Person
			placement="top-[72%] right-[50%]"
			name="Muhammad"
			cardHeader="Muhammad Farasat Abbas"
			cardPlacement="left-[60%] bottom-[80%]"
			pictureLink={new URL(
				'https://orbit.dtu.dk/files-asset/399011548/219052_3b80dbfd.jpg?w=160&f=webp'
			)}
		>
			<dl class="p-4">
				<dt>Modules</dt>
				<dd>Passive Components</dd>
				<dd class="mb-5">Environment</dd>
				<dt>
					<a
						class="link link-animated"
						href="https://orbit.dtu.dk/en/persons/muhammad-farasat-abbas/">Contact</a
					>
				</dt>
			</dl>
		</Person>
		<Person
			placement="top-[65%] right-[10%]"
			name="Intesar"
			cardHeader="Intesar Mahir"
			cardPlacement="right-[50%] bottom-[25%]"
		>
			<dl class="p-4">
				<dt>Teaching Assistant</dt>
			</dl>
		</Person>
		<Person
			placement="top-[30%] left-[60%]"
			name="Laura"
			cardHeader="Laura Sumper"
			cardPlacement="right-[40%]"
		>
			<dl class="p-4">
				<dt>Teaching Assistant</dt>
			</dl>
		</Person>
		<!-- <div class="pointer-events-auto absolute top-[10%] right-[60%] w-180">
			<NodeOverlay
				buttonExtraClasses="btn-secondary rounded-[50%]  h-50"
				cardExtraClasses="bg-secondary-container text-secondary-container-content left-[60%] text-4xl"
			>
				{#snippet buttonText()}
					Gabriel
				{/snippet}
				{#snippet header()}
					<Title id="gabriel">Tiberiu-Gabriel Zsurzsan</Title>
				{/snippet}
				<div class="flex flex-row gap-4">
					<img
						src="https://orbit.dtu.dk/files-asset/449238439/62516_1c2df3b4.jpg?w=160&f=webp"
						alt="Tiberiu-Gabriel Zsurzsan"
						class="h-auto w-40 mask-y-from-85% mask-y-to-100% mask-x-from-75% mask-x-to-100% object-contain opacity-70"
					/>

					<dl class="p-4">
						<dt>Module</dt>
						<dd class="mb-5">Printed Circuit Boards</dd>
						<dd class="mb-5">Course responsible</dd>
						<dt><a href="https://orbit.dtu.dk/en/persons/gabriel-zsurzsan/">Contact</a></dt>
					</dl>
				</div>
			</NodeOverlay>
		</div> -->
	</div>
</div>
