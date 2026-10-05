<script lang="ts">
	// const books = Array(8).fill(0);
	type Book = {
		title: string;
		author: string;
		comments?: string;
		link: string;
		image: string;
		alt: string;
	};
	const books: Book[] = [
		{
			title: 'Selvbestemmel-sesteorien',
			author: 'Ib Ravn',
			link: 'https://hansreitzel.dk/products/selvbestemmelsesteorien-bog-49710-9788741274461',
			image:
				'https://hansreitzel.dk/-/media/images/external.png?ei=https://multimediaserver.gyldendal.dk/HansReitzelred/CoverFace/WH_Original/9788741274461&w=320',
			alt: 'Add full reference'
		},
		{
			title: 'Skole uden prøver og karakterer',
			author: 'Noemi Katznelson, et al.',
			link: 'https://www.saxo.com/dk/skole-uden-proever-og-karakterer_bog_9788775730445?_gl=1*1tvsang*_up*MQ..*_gs*MQ..&gclid=Cj0KCQiAp-zLBhDkARIsABcYc6v8Pz2H8tcM748_yKdYMBgHaVga9otB487_Pmu33rScQfFyW1fiMekaAiqGEALw_wcB&gbraid=0AAAAAD_rHDWlJnzb1wXel1FABDAtPL3bR',
			image: 'https://imgcdn.saxo.com/_9788775730445',
			alt: 'Add full reference'
		},
		{
			title: 'Mærk Verden',
			author: 'Tore Nørretranders',
			link: 'https://www.saxo.com/dk/maerk-verden_tor-noerretranders_epub_9788702178524?srsltid=AU7gw4Uye4R2kILCoBZhaQ3Mtw9Q6sUEWN_uMv40z2kEGKyRnYwnYxoQ',
			image: 'https://imgcdn.saxo.com/_9788702178524',
			alt: 'Add full reference'
		},
		{
			title: 'Flow',
			author: 'Mihaly Csikszentmihalyi',
			comments: 'A book about achieving flow in life.',
			link: 'https://www.saxo.com/dk/flow-the-psychology-of-optimal-experience_paperback_9780061339202?srsltid=AU7gw4UFubHWIq065m_SWREZCULtPcHXLgG4p-aQ3-Z3yQo8b8mqmk71',
			image: 'https://imgcdn.saxo.com/_9780061339202',
			alt: 'Add full reference'
		},
		{
			title: 'Pseudoarbejde',
			author: 'Denis Nørmark & Anders Fogh Jensen',
			link: 'https://www.saxo.com/dk/pseudoarbejde_dennis-noermarkanders-fogh-jensen_haeftet_9788702245325?srsltid=AU7gw4XM3QbofIsKRSuAj_PE3UTQGFshjNhdBbQoscEbviDvHgHGH-jO',
			image: 'https://imgcdn.saxo.com/_9788702245325',
			alt: 'Add full reference'
		},
		{
			title: 'Tilbage på arbejde',
			author: 'Denis Nørmark',
			link: 'https://www.saxo.com/dk/tilbage-til-arbejdet_dennis-noermark_haeftet_9788702303612',
			image: 'https://imgcdn.saxo.com/_9788702303612',
			alt: 'Add full reference'
		},
		{
			title: 'Bullshit Jobs',
			author: 'David Graeber',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Atlas of the Heart',
			author: 'Brene Brown',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Følelsernes Bog',
			author: 'Torben Sangild',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Loving what is',
			author: 'Byron Katie',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Nonviolent Communication',
			author: 'Marshall B. Rosenberg',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Radical Honesty',
			author: 'Brad Blanton',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Homo Sapiens',
			author: 'Yuval Noah Harari',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Homo Deus',
			author: 'Yuval Noah Harari',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Regenerative Leadership',
			author: 'Giles Hutchins & Laura Storm',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Doughnut economics',
			author: 'Kate Raworth',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Nok',
			author: 'Toke Haunstrup',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Underskud',
			author: 'Emma Holten',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Coming Home to Who you Are',
			author: 'Mark Vandeneijnde & M. Aurelius Higgs',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Theory U',
			author: 'Otto Scharmer',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Braiding Sweetgrass',
			author: 'Robin Wall Kimmerer',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Hospicing Modernity',
			author: 'Vanesa Machado de Oliveira',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		}
	];
</script>

<div
	class="grid h-full w-full grid-cols-4 items-center justify-center justify-items-center gap-6 overflow-auto p-10"
>
	{#each books as book, index (index)}
		<div
			class=" bg-primary-container text-primary-container-content shadow-base-shadow h-100 w-80 overflow-hidden rounded-3xl shadow-lg"
		>
			{#if book.image !== '#'}
				<img src={book.image} alt={book.alt} class=" book-cover h-100 w-full rounded-t-3xl" />
			{:else}
				<div class="text-wrap">{book.title}</div>
				<div class="text-3xl text-wrap">{book.author}</div>
			{/if}
		</div>
	{/each}
</div>

<style>
	.book-cover {
		max-width: none;
		max-height: none;
		margin: 0;
		border: 0;
		display: block;
	}
</style>
