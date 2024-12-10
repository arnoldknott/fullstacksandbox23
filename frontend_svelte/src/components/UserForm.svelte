<script lang="ts">
	import '@material/web/textfield/filled-text-field.js';

	type Props = { type: 'login' | 'signup' };
	let { type }: Props = $props();
	const button = type === 'signup' ? 'Sign up' : 'Log in'; // untested!
</script>

<section class="flex h-full w-full justify-center">
	<div class="center py-12 md:w-8/12 lg:ml-6 lg:w-5/12">
		<div class="border-primary-400 rounded-2xl border-4 bg-blue-50 p-6">
			<form method="POST">
				<!-- Name input -->
				{#if type === 'signup'}
					<div class="relative mb-6">
						<md-filled-text-field
							label="Full Name"
							type="input"
							name="name"
							role="textbox"
							tabindex="0"
							class="mr-2 w-full"
						>
						</md-filled-text-field>
					</div>
				{/if}

				<!-- Email input -->
				<div class="relative mb-6">
					<md-filled-text-field
						label="Email"
						type="email"
						name="email"
						role="textbox"
						tabindex="0"
						class="mr-2 w-full"
					>
					</md-filled-text-field>
				</div>

				<!-- Password input -->
				<div class="relative mb-6">
					<md-filled-text-field
						label="Password"
						type="password"
						name="password"
						role="textbox"
						tabindex="0"
						class="mr-2 w-full"
					>
					</md-filled-text-field>
				</div>

				<!-- Submit button -->
				<div class="text-center">
					<button
						type="submit"
						class="inline-block w-5/6 rounded bg-blue-400 px-7 pb-2.5 pt-3 uppercase leading-normal text-white shadow-[0_4px_9px_-4px_#3b71ca] transition duration-150 ease-in-out hover:bg-blue-700 hover:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] focus:bg-blue-600 focus:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] focus:outline-none focus:ring-0 active:bg-blue-700 active:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.3),0_4px_18px_0_rgba(59,113,202,0.2)] dark:shadow-[0_4px_9px_-4px_rgba(59,113,202,0.5)] dark:hover:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)] dark:focus:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)] dark:active:shadow-[0_8px_9px_-4px_rgba(59,113,202,0.2),0_4px_18px_0_rgba(59,113,202,0.1)]"
						data-te-ripple-init
						data-te-ripple-color="light"
					>
						{button}
					</button>
				</div>
			</form>
		</div>
	</div>
</section>
