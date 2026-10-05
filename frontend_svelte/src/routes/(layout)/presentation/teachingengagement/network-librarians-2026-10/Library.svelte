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
			link: 'https://www.saxo.com/dk/bullshit-jobs_paperback_9780141983479?srsltid=AU7gw4Xw-NbzTZpF4D0wnU9U1HCUZxcBnrzqyz7XgXXcPIyeKl8DeRDE',
			image: 'https://imgcdn.saxo.com/_9780141983479',
			alt: 'Add full reference'
		},
		{
			title: 'Atlas of the Heart',
			author: 'Brene Brown',
			link: 'https://www.saxo.com/dk/atlas-of-the-heart_brene-brown_hardback_9781785043772?srsltid=AU7gw4Wh5d-naPRZPUi8DZTNk_aSSk33aRBR8tHsi6idI0Yc7uwV67vE',
			image: 'https://imgcdn.saxo.com/_9781785043772',
			alt: 'Add full reference'
		},
		{
			title: 'Følelsernes Bog',
			author: 'Torben Sangild',
			link: 'https://www.bog-ide.dk/products/foelelsernes-bog-torben-sangild-paperback-3178195?srsltid=AU7gw4VUMGLlJwDFGpm9CB0BqwfhpbGGh32d2SVGPz0rieyHDQ9KdeuT',
			image: 'https://www.bog-ide.dk/cdn/shop/files/3178195_COVER.jpg?v=1773495194&width=600',
			alt: 'Add full reference'
		},
		{
			title: 'Loving what is',
			author: 'Byron Katie',
			link: 'https://www.saxo.com/dk/loving-what-is_paperback_9780712629300?srsltid=AU7gw4Uw_OpOoaZGcPseiK34vJJI_0bx_5EiKVPczwa9tzt3ntFaOquj',
			image: 'https://imgcdn.saxo.com/_9780712629300',
			alt: 'Add full reference'
		},
		{
			title: 'Nonviolent Communication',
			author: 'Marshall B. Rosenberg',
			link: 'https://www.saxo.com/dk/nonviolent-communication-3-e_marshall-b-rosenberg_paperback_9781892005281?srsltid=AU7gw4UQ9qcMfQgTgg_HXTkUpH4DX2kMf2Rqq_pF8AaJYU-Xtz85GQ3g',
			image: 'https://imgcdn.saxo.com/_9781892005281',
			alt: 'Add full reference'
		},
		{
			title: 'Radical Honesty',
			author: 'Brad Blanton',
			link: 'https://www.saxo.com/dk/radical-honesty_brad-blanton_paperback_9780440507543?srsltid=AU7gw4WnJ7-4l-z_Y7EXkhqFP5OqOWMyPV_2l6Qs4sgj6ayhgD2PZGjg',
			image: 'https://imgcdn.saxo.com/_9780440507543',
			alt: 'Add full reference'
		},
		{
			title: 'Homo Sapiens',
			author: 'Yuval Noah Harari',
			link: 'https://www.saxo.com/dk/sapiens-en-kort-historie-om-menneskeheden_bog_9788727022710?srsltid=AU7gw4V7n0b471Dmsn5j7HBDxhyNNqJZpSiyXpO2jX8Nl-VimWAZrPDg',
			image: 'https://imgcdn.saxo.com/_9788727022710',
			alt: 'Add full reference'
		},
		{
			title: 'Homo Deus',
			author: 'Yuval Noah Harari',
			link: 'https://www.saxo.com/dk/homo-deus-a-brief-history-of-tomorrow-pb-b-format_yuval-noah-harari_paperback_9781784703936?srsltid=AU7gw4VriMtWvdoQMVQpNA2C1AZ35Rlvrs1M0NUZ_BzLI4zZnGQKXmp4',
			image: 'https://imgcdn.saxo.com/_9781784703936',
			alt: 'Add full reference'
		},
		{
			title: 'Regenerative Leadership',
			author: 'Giles Hutchins & Laura Storm',
			link: 'https://www.saxo.com/dk/regenerative-leadership_giles-hutchins-laura-storm_paperback_9781783241194?srsltid=AU7gw4VEABCk3onUbfSsUXa4M7NiJ6ZHfuZ7kPxW_C6SfB0xCXL9P4i1',
			image: 'https://imgcdn.saxo.com/_9781783241194',
			alt: 'Add full reference'
		},
		{
			title: 'Doughnut economics',
			author: 'Kate Raworth',
			link: 'https://www.saxo.com/dk/doughnut-economics-seven-ways-to-think-like-a-21st-century-economist-pb-b-format_paperback_9781847941398?srsltid=AU7gw4WNqUOvOxQOT6E9Cgs9YWFY7L7y7I4CPGx7Awz11UULEPPeA_Z-',
			image: 'https://imgcdn.saxo.com/_9781847941398',
			alt: 'Add full reference'
		},
		{
			title: 'Nok',
			author: 'Toke Haunstrup',
			link: 'https://www.saxo.com/dk/nok_bog_9788797628607?srsltid=AU7gw4VrcT_NmDNQAEyUvyamqGJj11OVOApXceIgjmaRKnOvAOjM3fNL',
			image: 'https://imgcdn.saxo.com/_9788797628607',
			alt: 'Add full reference'
		},
		{
			title: 'Underskud',
			author: 'Emma Holten',
			link: 'https://www.saxo.com/dk/underskud_bog_9788740074130?srsltid=AU7gw4UvKQkoGobVtD8L6YfckWtBok4iftl5wepJxuQZM2Rg2e1Nnffd',
			image: 'https://imgcdn.saxo.com/_9788740074130',
			alt: 'Add full reference'
		},
		{
			title: 'Coming Home to Who you Are - Education Reenlightened',
			author: 'Mark Vandeneijnde & M. Aurelius Higgs',
			link: 'https://www.amazon.com/Coming-Home-Who-You-ReEnlightened/dp/B0DYNQ1KVP',
			image: 'https://m.media-amazon.com/images/I/71SS3cQY-ZL._SY466_.jpg',
			alt: 'Add full reference'
		},
		{
			title: 'Theory U',
			author: 'Otto Scharmer',
			link: 'https://www.saxo.com/dk/theory-u-leading-from-the-future-as-it-emerges_c-otto-scharmer_hardback_9781626567986?srsltid=AU7gw4XUTtrxNmVromaIR8Tlh-1Blun7aoDREghU7HRXwOfgaJowri1k',
			image: 'https://imgcdn.saxo.com/_9781626567986',
			alt: 'Add full reference'
		},
		{
			title: 'Braiding Sweetgrass',
			author: 'Robin Wall Kimmerer',
			link: 'https://www.amazon.com/Braiding-Sweetgrass-Indigenous-Scientific-Knowledge/dp/1571313567',
			image: 'https://m.media-amazon.com/images/I/71OgjPcg6-L._SY466_.jpg',
			alt: 'Add full reference'
		},
		{
			title: 'Hospicing Modernity',
			author: 'Vanesa Machado de Oliveira',
			link: 'https://www.northatlanticbooks.com/shop/hospicing-modernity/',
			image: 'https://www.northatlanticbooks.com/wp-content/uploads/books/hospicing-modernity.png',
			alt: 'Add full reference'
		},
		{
			title: 'The Art of Regenerative Educatorship',
			author: 'Mieke Lopes Cardozo, Koen Wessels, Bas van den Berg',
			link: 'https://www.routledge.com/The-Art-of-Regenerative-Educatorship-A-Developmental-Guide/LopesCardozo-Wessels-Berg/p/book/9789048570522',
			image: 'https://images.routledge.com/common/jackets/crclarge/978904857/9789048570522.jpg',
			alt: 'Add full reference'
		},
		{
			title: 'Learning as if Life Depended on It',
			author: 'Olli-Pekka Heinonen',
			link: 'https://www.penguinrandomhouse.com/books/821963/learning-as-if-life-depended-on-it-by-olli-pekka-heinonen/',
			image: 'https://images3.penguinrandomhouse.com/cover/9781914568077',
			alt: 'Add full reference'
		},
	];
</script>

<div
	class="grid h-full w-full grid-cols-5 items-center justify-center justify-items-center gap-x-6 gap-y-10 overflow-auto p-10"
>
	{#each books as book, index (index)}
		<div
			class=" bg-primary-container text-primary-container-content shadow-base-shadow h-90 w-65 overflow-hidden rounded-3xl shadow-lg"
		>
			{#if book.image !== '#'}
				<img src={book.image} alt={book.alt} class="book-cover h-100 w-full rounded-t-3xl object-stretch" />
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
