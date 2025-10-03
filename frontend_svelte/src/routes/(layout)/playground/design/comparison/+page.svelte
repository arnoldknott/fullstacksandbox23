<script lang="ts">
	import Heading from '$components/Heading.svelte';
	import { initAccordion } from '$lib/userInterface';
	import AccordionItem from '../AccordionItem.svelte';
	import ColorTiles from './ColorTiles.svelte';
</script>

<div class="grid w-full grid-cols-1 gap-4 xl:grid-cols-2">
	<div class="col-span-2">
		<Heading>Colors</Heading>
		<p class="title text-center text-2xl">Color matching Material Design => FlyonUI:</p>
		<div
			class="accordion accordion-bordered divide-y"
			data-accordion-always-open=""
			{@attach initAccordion}
		>
			<AccordionItem title="Foreground Colors">
				<div class="grid grid-cols-2 gap-2">
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-primary',
							color: '--md-sys-color-on-primary',
							name: 'primary'
						}}
						flyonUIClasses={{
							bg: 'bg-primary',
							text: 'text-primary-content',
							name: 'primary'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-primary',
							color: '--md-sys-color-primary',
							name: 'onPrimary'
						}}
						flyonUIClasses={{
							bg: 'bg-primary-content',
							text: 'text-primary',
							name: 'primary-content'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-primary-container',
							color: '--md-sys-color-on-primary-container',
							name: 'primary container'
						}}
						flyonUIClasses={{
							bg: 'bg-primary-container',
							text: 'text-primary-container-content',
							name: 'primary-container'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-primary-container',
							color: '--md-sys-color-primary-container',
							name: 'onPrimary container'
						}}
						flyonUIClasses={{
							bg: 'bg-primary-container-content',
							text: 'text-primary-container',
							name: 'primary-container-content'
						}}
					/>
					<hr class="col-span-2" />
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-secondary',
							color: '--md-sys-color-on-secondary',
							name: 'secondary'
						}}
						flyonUIClasses={{
							bg: 'bg-secondary',
							text: 'text-secondary-content',
							name: 'secondary'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-secondary',
							color: '--md-sys-color-secondary',
							name: 'onSecondary'
						}}
						flyonUIClasses={{
							bg: 'bg-secondary-content',
							text: 'text-secondary',
							name: 'secondary-content'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-secondary-container',
							color: '--md-sys-color-on-secondary-container',
							name: 'secondary container'
						}}
						flyonUIClasses={{
							bg: 'bg-secondary-container',
							text: 'text-secondary-container-content',
							name: 'secondary-container'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-secondary-container',
							color: '--md-sys-color-secondary-container',
							name: 'onSecondary container'
						}}
						flyonUIClasses={{
							bg: 'bg-secondary-container-content',
							text: 'text-secondary-container',
							name: 'secondary-container-content'
						}}
					/>
					<hr class="col-span-2" />
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-tertiary',
							color: '--md-sys-color-on-tertiary',
							name: 'tertiary'
						}}
						flyonUIClasses={{
							bg: 'bg-accent',
							text: 'text-accent-content',
							name: 'accent'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-tertiary',
							color: '--md-sys-color-tertiary',
							name: 'onTertiary'
						}}
						flyonUIClasses={{
							bg: 'bg-accent-content',
							text: 'text-accent',
							name: 'accent-content'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-tertiary-container',
							color: '--md-sys-color-on-tertiary-container',
							name: 'tertiary container'
						}}
						flyonUIClasses={{
							bg: 'bg-accent-container',
							text: 'text-accent-container-content',
							name: 'accent-container'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-tertiary-container',
							color: '--md-sys-color-tertiary-container',
							name: 'onTertiary container'
						}}
						flyonUIClasses={{
							bg: 'bg-accent-container-content',
							text: 'text-accent-container',
							name: 'accent-container-content'
						}}
					/>
					<hr class="col-span-2" />
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-neutral',
							color: '--md-sys-color-on-neutral',
							name: 'neutral'
						}}
						flyonUIClasses={{
							bg: 'bg-neutral',
							text: 'text-neutral-content',
							name: 'neutral'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-neutral',
							color: '--md-sys-color-neutral',
							name: 'onNeutral'
						}}
						flyonUIClasses={{
							bg: 'bg-neutral-content',
							text: 'text-neutral',
							name: 'neutral-content'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-neutral-container',
							color: '--md-sys-color-on-neutral-container',
							name: 'neutral container'
						}}
						flyonUIClasses={{
							bg: 'bg-neutral-container',
							text: 'text-neutral-container-content',
							name: 'neutral-container'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-neutral-container',
							color: '--md-sys-color-neutral-container',
							name: 'onNeutral container'
						}}
						flyonUIClasses={{
							bg: 'bg-neutral-container-content',
							text: 'text-neutral-container',
							name: 'neutral-container-content'
						}}
					/>
					<hr class="col-span-2" />
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-info',
							color: '--md-sys-color-on-info',
							name: 'info'
						}}
						flyonUIClasses={{
							bg: 'bg-info',
							text: 'text-info-content',
							name: 'info'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-info',
							color: '--md-sys-color-info',
							name: 'onInfo'
						}}
						flyonUIClasses={{
							bg: 'bg-info-content',
							text: 'text-info',
							name: 'info-content'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-info-container',
							color: '--md-sys-color-on-info-container',
							name: 'info container'
						}}
						flyonUIClasses={{
							bg: 'bg-info-container',
							text: 'text-info-container-content',
							name: 'info-container'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-info-container',
							color: '--md-sys-color-info-container',
							name: 'onInfo container'
						}}
						flyonUIClasses={{
							bg: 'bg-info-container-content',
							text: 'text-info-container',
							name: 'info-container-content'
						}}
					/>
					<hr class="col-span-2" />
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-success',
							color: '--md-sys-color-on-success',
							name: 'success'
						}}
						flyonUIClasses={{
							bg: 'bg-success',
							text: 'text-success-content',
							name: 'success'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-success',
							color: '--md-sys-color-success',
							name: 'onSuccess'
						}}
						flyonUIClasses={{
							bg: 'bg-success-content',
							text: 'text-success',
							name: 'success-content'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-success-container',
							color: '--md-sys-color-on-success-container',
							name: 'success container'
						}}
						flyonUIClasses={{
							bg: 'bg-success-container',
							text: 'text-success-container-content',
							name: 'success-container'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-success-container',
							color: '--md-sys-color-success-container',
							name: 'onSuccess container'
						}}
						flyonUIClasses={{
							bg: 'bg-success-container-content',
							text: 'text-success-container',
							name: 'success-container-content'
						}}
					/>
					<hr class="col-span-2" />
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-warning',
							color: '--md-sys-color-on-warning',
							name: 'warning'
						}}
						flyonUIClasses={{
							bg: 'bg-warning',
							text: 'text-warning-content',
							name: 'warning'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-warning',
							color: '--md-sys-color-warning',
							name: 'onWarning'
						}}
						flyonUIClasses={{
							bg: 'bg-warning-content',
							text: 'text-warning',
							name: 'warning-content'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-warning-container',
							color: '--md-sys-color-on-warning-container',
							name: 'warning container'
						}}
						flyonUIClasses={{
							bg: 'bg-warning-container',
							text: 'text-warning-container-content',
							name: 'warning-container'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-warning-container',
							color: '--md-sys-color-warning-container',
							name: 'onWarning container'
						}}
						flyonUIClasses={{
							bg: 'bg-warning-container-content',
							text: 'text-warning-container',
							name: 'warning-container-content'
						}}
					/>
					<hr class="col-span-2" />
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-error',
							color: '--md-sys-color-on-error',
							name: 'error'
						}}
						flyonUIClasses={{
							bg: 'bg-error',
							text: 'text-error-content',
							name: 'error'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-error',
							color: '--md-sys-color-error',
							name: 'onError'
						}}
						flyonUIClasses={{
							bg: 'bg-error-content',
							text: 'text-error',
							name: 'error-content'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-error-container',
							color: '--md-sys-color-on-error-container',
							name: 'error container'
						}}
						flyonUIClasses={{
							bg: 'bg-error-container',
							text: 'text-error-container-content',
							name: 'error-container'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-error-container',
							color: '--md-sys-color-error-container',
							name: 'onError container'
						}}
						flyonUIClasses={{
							bg: 'bg-error-container-content',
							text: 'text-error-container',
							name: 'error-container-content'
						}}
					/>
				</div>
			</AccordionItem>
			<AccordionItem title="Background Colors">
				<div class="grid grid-cols-2 gap-2">
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-surface-container-lowest',
							color: '--md-sys-color-on-surface',
							name: 'surface container lowest'
						}}
						flyonUIClasses={{
							bg: 'bg-base-100',
							text: 'text-base-content',
							name: 'base-100'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-surface-container-low',
							color: '--md-sys-color-on-surface',
							name: 'surface container low'
						}}
						flyonUIClasses={{
							bg: 'bg-base-150',
							text: 'text-base-content',
							name: 'base-150'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-surface-container',
							color: '--md-sys-color-on-surface',
							name: 'surface container'
						}}
						flyonUIClasses={{
							bg: 'bg-base-200',
							text: 'text-base-content',
							name: 'base-200'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-surface-container-high',
							color: '--md-sys-color-on-surface',
							name: 'surface container high'
						}}
						flyonUIClasses={{
							bg: 'bg-base-250',
							text: 'text-base-content',
							name: 'base-250'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-surface-container-highest',
							color: '--md-sys-color-on-surface',
							name: 'surface container highest'
						}}
						flyonUIClasses={{
							bg: 'bg-base-300',
							text: 'text-base-content',
							name: 'base-300'
						}}
					/>
					<hr class="col-span-2" />
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-on-surface',
							color: '--md-sys-color-surface',
							name: 'on surface'
						}}
						flyonUIClasses={{
							bg: 'bg-base-content',
							text: 'text-base-100',
							name: 'base-content'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-shadow',
							color: '--md-sys-color-on-surface',
							name: 'shadow'
						}}
						flyonUIClasses={{
							bg: 'bg-base-shadow',
							text: 'text-base-content',
							name: 'base-shadow'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-outline',
							color: '--md-sys-color-on-surface',
							name: 'outline'
						}}
						flyonUIClasses={{
							bg: 'bg-outline',
							text: 'text-base-content',
							name: 'outline'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-inverse-surface',
							color: '--md-sys-color-inverse-on-surface',
							name: 'inverse surface'
						}}
						flyonUIClasses={{
							bg: 'bg-inverse-surface',
							text: 'text-inverse-surface-content',
							name: 'inverse-surface'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-scrim',
							color: '--md-sys-color-on-scrim',
							name: 'scrim'
						}}
						flyonUIClasses={{
							bg: 'bg-scrim',
							text: 'text-scrim-content',
							name: 'scrim'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-background',
							color: '--md-sys-color-on-background',
							name: 'background'
						}}
						flyonUIClasses={{
							bg: 'bg-background',
							text: 'text-background-content',
							name: 'background'
						}}
					/>
				</div>
			</AccordionItem>
			<AccordionItem title="Other Colors">
				<div class="grid grid-cols-2 gap-2">
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-inverse-primary',
							color: '--md-sys-color-on-inverse-primary',
							name: 'inverse primary'
						}}
						flyonUIClasses={{
							bg: 'bg-inverse-primary',
							text: 'text-inverse-primary-content',
							name: 'inverse-primary'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-neutral-palette-key-color',
							color: '--md-sys-color-on-neutral-palette-key-color',
							name: 'neutral palette key color'
						}}
						flyonUIClasses={{
							bg: 'bg-neutral-palette-key-color',
							text: 'text-neutral-palette-key-color-content',
							name: 'neutral-palette-key-color'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-neutral-variant-palette-key-color',
							color: '--md-sys-color-on-neutral-variant-palette-key-color',
							name: 'neutral variant palette key color'
						}}
						flyonUIClasses={{
							bg: 'bg-neutral-variant-palette-key-color',
							text: 'text-neutral-variant-palette-key-color-content',
							name: 'neutral-variant-palette-key-color'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-primary-palette-key-color',
							color: '--md-sys-color-on-primary-palette-key-color',
							name: 'primary palette key color'
						}}
						flyonUIClasses={{
							bg: 'bg-primary-palette-key-color',
							text: 'text-primary-palette-key-color-content',
							name: 'primary-palette-key-color'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-secondary-palette-key-color',
							color: '--md-sys-color-on-secondary-palette-key-color',
							name: 'secondary palette key color'
						}}
						flyonUIClasses={{
							bg: 'bg-secondary-palette-key-color',
							text: 'text-secondary-palette-key-color-content',
							name: 'secondary-palette-key-color'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-tertiary-palette-key-color',
							color: '--md-sys-color-on-tertiary-palette-key-color',
							name: 'tertiary palette key color'
						}}
						flyonUIClasses={{
							bg: 'bg-accent-palette-key-color',
							text: 'text-accent-palette-key-color-content',
							name: 'accent-palette-key-color'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-primary-fixed',
							color: '--md-sys-color-on-primary-fixed',
							name: 'primary fixed'
						}}
						flyonUIClasses={{
							bg: 'bg-primary-fixed',
							text: 'text-primary-fixed-content',
							name: 'primary-fixed'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-primary-fixed-dim',
							color: '--md-sys-color-on-primary-fixed-dim',
							name: 'primary fixed dim'
						}}
						flyonUIClasses={{
							bg: 'bg-primary-fixed-dim',
							text: 'text-primary-fixed-dim-content',
							name: 'primary-fixed-dim'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-secondary-fixed',
							color: '--md-sys-color-on-secondary-fixed',
							name: 'secondary fixed'
						}}
						flyonUIClasses={{
							bg: 'bg-secondary-fixed',
							text: 'text-secondary-fixed-content',
							name: 'secondary-fixed'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-secondary-fixed-dim',
							color: '--md-sys-color-on-secondary-fixed-dim',
							name: 'secondary fixed dim'
						}}
						flyonUIClasses={{
							bg: 'bg-secondary-fixed-dim',
							text: 'text-secondary-fixed-dim-content',
							name: 'secondary-fixed-dim'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-tertiary-fixed',
							color: '--md-sys-color-on-tertiary-fixed',
							name: 'tertiary fixed'
						}}
						flyonUIClasses={{
							bg: 'bg-accent-fixed',
							text: 'text-accent-fixed-content',
							name: 'accent-fixed'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-tertiary-fixed-dim',
							color: '--md-sys-color-on-tertiary-fixed-dim',
							name: 'tertiary fixed dim'
						}}
						flyonUIClasses={{
							bg: 'bg-accent-fixed-dim',
							text: 'text-accent-fixed-dim-content',
							name: 'accent-fixed-dim'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-surface-dim',
							color: '--md-sys-color-on-surface-dim',
							name: 'surface dim'
						}}
						flyonUIClasses={{
							bg: 'bg-surface-dim',
							text: 'text-surface-dim-content',
							name: 'surface-dim'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-surface',
							color: '--md-sys-color-on-surface',
							name: 'surface'
						}}
						flyonUIClasses={{
							bg: 'bg-surface',
							text: 'text-surface-content',
							name: 'surface'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-surface-bright',
							color: '--md-sys-color-on-surface-bright',
							name: 'surface bright'
						}}
						flyonUIClasses={{
							bg: 'bg-surface-bright',
							text: 'text-surface-bright-content',
							name: 'surface-bright'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-surface-variant',
							color: '--md-sys-color-on-surface-variant',
							name: 'surface variant'
						}}
						flyonUIClasses={{
							bg: 'bg-surface-variant',
							text: 'text-surface-variant-content',
							name: 'surface-variant'
						}}
					/>
					<ColorTiles
						materialVariables={{
							background: '--md-sys-color-surface-tint',
							color: '--md-sys-color-on-surface-tint',
							name: 'surface tint'
						}}
						flyonUIClasses={{
							bg: 'bg-surface-tint',
							text: 'text-surface-tint-content',
							name: 'surface-tint'
						}}
					/>
				</div>
			</AccordionItem>
		</div>
	</div>
</div>
