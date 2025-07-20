<div class="flex w-full justify-center">
	<div class="flex flex-col justify-center">
		<div class="heading-large md:display-small text-primary italic" style="line-height: 1;">
			Fullstack
		</div>
		<div
			class="heading-large text-secondary font-bold tracking-wide md:tracking-widest"
			style="line-height: 1"
		>
			Sandbox
		</div>
	</div>
	<div class="text-accent ml-3 flex items-center text-[116px]">23</div>
	<div>
		Repeating the bug of creating the image with the tag of the latest main commit sha, even though
		no commit to main, but infrastructure was updated.
	</div>
	<ul>
		<li>
			Repeating the false tagging behavior: changed containerApps.tf, frontend_svelte.yml and this
			file.
		</li>
		<li>
			Changed the containerApps.tf file to have a comment in it, so that the file is changed and now
			variables are echoed in the frontend_svelte.yml and backend.yml file.
		</li>
	</ul>
</div>
