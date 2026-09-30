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
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Skole uden prøver og karakterer',
			author: 'Noemi Katznelson, et al.',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Mærk Verden',
			author: 'Tore Nørretranders',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Flow',
			author: 'Mihaly Csikszentmihalyi',
			comments: 'A book about achieving flow in life.',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Pseudoarbejde',
			author: 'Denis Nørmark & Anders Fogh Jensen',
			link: '#',
			image: '#',
			alt: 'Add full reference'
		},
		{
			title: 'Tilbage på arbejde',
			author: 'Denis Nørmark',
			link: '#',
			image: '#',
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
			class="bg-primary-container text-primary-container-content shadow-base-shadow h-100 w-80 rounded-3xl shadow-lg"
		>
			<div class="text-wrap">{book.title}</div>
			<div class="text-3xl text-wrap">{book.author}</div>
		</div>
	{/each}
</div>
