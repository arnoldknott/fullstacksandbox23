<script lang="ts" module>
	export type BookType = {
		id: string;
		title: string;
		author: string;
		link: string;
		image: string;
		alt: string;
		comments?: string[];
	};
</script>

<script lang="ts">
	import Icon from '@iconify/svelte';
	import { flip } from 'svelte/animate';

	import { Action } from '$lib/accessHandler';
	import type { SocketIO } from '$lib/socketio.svelte';
	import type { MessageExtended } from '$lib/types';

	import Book from './Book.svelte';
	import CardOverlay from './CardOverlay.svelte';

	let { socketio, questionid }: { socketio?: SocketIO<MessageExtended>; questionid?: string } =
		$props();

	let booksAnswersSorted = $derived(socketio?.getSelectedEntities('sortedBooksAnswers') ?? []);

	const providedBooks: BookType[] = [
		{
			id: 'selvbestemmelsesteorien',
			title: 'Selvbestemmelsesteorien',
			author: 'Ib Ravn',
			link: 'https://hansreitzel.dk/products/selvbestemmelsesteorien-bog-49710-9788741274461',
			image:
				'https://hansreitzel.dk/-/media/images/external.png?ei=https://multimediaserver.gyldendal.dk/HansReitzelred/CoverFace/WH_Original/9788741274461&w=320',
			alt: 'Ravn, Ib (2021). Selvbestemmelsesteorien. Hans Reitzels Forlag. ISBN: 9788741274461.'
		},
		{
			id: 'skole-uden-proever-og-karakterer',
			title: 'Skole uden prøver og karakterer',
			author: 'Noemi Katznelson, et al.',
			link: 'https://www.saxo.com/dk/skole-uden-proever-og-karakterer_bog_9788775730445?_gl=1*1tvsang*_up*MQ..*_gs*MQ..&gclid=Cj0KCQiAp-zLBhDkARIsABcYc6v8Pz2H8tcM748_yKdYMBgHaVga9otB487_Pmu33rScQfFyW1fiMekaAiqGEALw_wcB&gbraid=0AAAAAD_rHDWlJnzb1wXel1FABDAtPL3bR',
			image: 'https://imgcdn.saxo.com/_9788775730445',
			alt: 'Katznelson, Noemi, Sørensen, Niels Ulrik, Neergaard, Marie, Krogh, Søren Christian, Louw, Arnt, & Marstrand, Barbara (2025). Skole uden prøver og karakterer: Om motivation og feedback på fri- og efterskoler, der arbejder med prøve- og karakterfrihed. Aalborg Universitetsforlag. ISBN: 9788775730445.'
		},
		{
			id: 'maerk-verden',
			title: 'Mærk Verden',
			author: 'Tore Nørretranders',
			link: 'https://www.saxo.com/dk/maerk-verden_tor-noerretranders_epub_9788702178524?srsltid=AU7gw4Uye4R2kILCoBZhaQ3Mtw9Q6sUEWN_uMv40z2kEGKyRnYwnYxoQ',
			image: 'https://imgcdn.saxo.com/_9788702178524',
			alt: 'Nørretranders, Tor (2015). Mærk verden: En beretning om bevidsthed [E-bog]. Gyldendal. ISBN: 9788702178524.'
		},
		{
			id: 'flow',
			title: 'Flow',
			author: 'Mihaly Csikszentmihalyi',
			link: 'https://www.saxo.com/dk/flow-the-psychology-of-optimal-experience_paperback_9780061339202?srsltid=AU7gw4UFubHWIq065m_SWREZCULtPcHXLgG4p-aQ3-Z3yQo8b8mqmk71',
			image: 'https://imgcdn.saxo.com/_9780061339202',
			alt: 'Csikszentmihalyi, Mihaly (2008). Flow: The Psychology of Optimal Experience. HarperCollins. ISBN: 9780061339202.'
		},
		{
			id: 'pseudoarbejde',
			title: 'Pseudoarbejde',
			author: 'Denis Nørmark & Anders Fogh Jensen',
			link: 'https://www.saxo.com/dk/pseudoarbejde_dennis-noermarkanders-fogh-jensen_haeftet_9788702245325?srsltid=AU7gw4XM3QbofIsKRSuAj_PE3UTQGFshjNhdBbQoscEbviDvHgHGH-jO',
			image: 'https://imgcdn.saxo.com/_9788702245325',
			alt: 'Nørmark, Dennis, & Jensen, Anders Fogh (2018). Pseudoarbejde: Hvordan vi fik travlt med at lave ingenting. Gyldendal Business. ISBN: 9788702245325.'
		},
		{
			id: 'tilbage-paa-arbejde',
			title: 'Tilbage på arbejde',
			author: 'Denis Nørmark',
			link: 'https://www.saxo.com/dk/tilbage-til-arbejdet_dennis-noermark_haeftet_9788702303612',
			image: 'https://imgcdn.saxo.com/_9788702303612',
			alt: 'Nørmark, Dennis (2021). Tilbage til arbejdet: Sådan bekæmper vi pseudoarbejde i organisationer. Gyldendal Business. ISBN: 9788702303612.'
		},
		{
			id: 'bullshit-jobs',
			title: 'Bullshit Jobs',
			author: 'David Graeber',
			link: 'https://www.saxo.com/dk/bullshit-jobs_paperback_9780141983479?srsltid=AU7gw4Xw-NbzTZpF4D0wnU9U1HCUZxcBnrzqyz7XgXXcPIyeKl8DeRDE',
			image: 'https://imgcdn.saxo.com/_9780141983479',
			alt: 'Graeber, David (2019). Bullshit Jobs: The Rise of Pointless Work, and What We Can Do About It. Penguin Books. ISBN: 9780141983479.'
		},
		{
			id: 'atlas-of-the-heart',
			title: 'Atlas of the Heart',
			author: 'Brene Brown',
			link: 'https://www.saxo.com/dk/atlas-of-the-heart_brene-brown_hardback_9781785043772?srsltid=AU7gw4Wh5d-naPRZPUi8DZTNk_aSSk33aRBR8tHsi6idI0Yc7uwV67vE',
			image: 'https://imgcdn.saxo.com/_9781785043772',
			alt: 'Brown, Brené (2021). Atlas of the Heart: Mapping Meaningful Connection and the Language of Human Experience. Vermilion. ISBN: 9781785043772.'
		},
		{
			id: 'foelelsernes-bog',
			title: 'Følelsernes Bog',
			author: 'Torben Sangild',
			link: 'https://www.bog-ide.dk/products/foelelsernes-bog-torben-sangild-paperback-3178195?srsltid=AU7gw4VUMGLlJwDFGpm9CB0BqwfhpbGGh32d2SVGPz0rieyHDQ9KdeuT',
			image: 'https://www.bog-ide.dk/cdn/shop/files/3178195_COVER.jpg?v=1773495194&width=600',
			alt: 'Sangild, Torben (2024). Følelsernes bog. Zetland Bøger. ISBN: 9788793761513.'
		},
		{
			id: 'loving-what-is',
			title: 'Loving what is',
			author: 'Byron Katie',
			link: 'https://www.saxo.com/dk/loving-what-is_paperback_9780712629300?srsltid=AU7gw4Uw_OpOoaZGcPseiK34vJJI_0bx_5EiKVPczwa9tzt3ntFaOquj',
			image: 'https://imgcdn.saxo.com/_9780712629300',
			alt: 'Katie, Byron, & Mitchell, Stephen (2002). Loving What Is: Four Questions That Can Change Your Life. Rider & Co. ISBN: 9780712629300.'
		},
		{
			id: 'nonviolent-communication',
			title: 'Nonviolent Communication',
			author: 'Marshall B. Rosenberg',
			link: 'https://www.saxo.com/dk/nonviolent-communication-3-e_marshall-b-rosenberg_paperback_9781892005281?srsltid=AU7gw4UQ9qcMfQgTgg_HXTkUpH4DX2kMf2Rqq_pF8AaJYU-Xtz85GQ3g',
			image: 'https://imgcdn.saxo.com/_9781892005281',
			alt: 'Rosenberg, Marshall B. (2015). Nonviolent Communication: A Language of Life (3rd ed.). PuddleDancer Press. ISBN: 9781892005281.'
		},
		{
			id: 'radical-honesty',
			title: 'Radical Honesty',
			author: 'Brad Blanton',
			link: 'https://www.saxo.com/dk/radical-honesty_brad-blanton_paperback_9780440507543?srsltid=AU7gw4WnJ7-4l-z_Y7EXkhqFP5OqOWMyPV_2l6Qs4sgj6ayhgD2PZGjg',
			image: 'https://imgcdn.saxo.com/_9780440507543',
			alt: 'Blanton, Brad (1996). Radical Honesty: How to Transform Your Life by Telling the Truth. Random House. ISBN: 9780440507543.'
		},
		{
			id: 'homo-sapiens',
			title: 'Homo Sapiens',
			author: 'Yuval Noah Harari',
			link: 'https://www.saxo.com/dk/sapiens-en-kort-historie-om-menneskeheden_bog_9788727022710?srsltid=AU7gw4V7n0b471Dmsn5j7HBDxhyNNqJZpSiyXpO2jX8Nl-VimWAZrPDg',
			image: 'https://imgcdn.saxo.com/_9788727022710',
			alt: 'Harari, Yuval Noah (2024). Sapiens: En kort historie om menneskeheden. Lindhardt og Ringhof. ISBN: 9788727022710.'
		},
		{
			id: 'homo-deus',
			title: 'Homo Deus',
			author: 'Yuval Noah Harari',
			link: 'https://www.saxo.com/dk/homo-deus-a-brief-history-of-tomorrow-pb-b-format_yuval-noah-harari_paperback_9781784703936?srsltid=AU7gw4VriMtWvdoQMVQpNA2C1AZ35Rlvrs1M0NUZ_BzLI4zZnGQKXmp4',
			image: 'https://imgcdn.saxo.com/_9781784703936',
			alt: 'Harari, Yuval Noah (2017). Homo Deus: A Brief History of Tomorrow. Vintage. ISBN: 9781784703936.'
		},
		{
			id: 'regenerative-leadership',
			title: 'Regenerative Leadership',
			author: 'Giles Hutchins & Laura Storm',
			link: 'https://www.saxo.com/dk/regenerative-leadership_giles-hutchins-laura-storm_paperback_9781783241194?srsltid=AU7gw4VEABCk3onUbfSsUXa4M7NiJ6ZHfuZ7kPxW_C6SfB0xCXL9P4i1',
			image: 'https://imgcdn.saxo.com/_9781783241194',
			alt: 'Hutchins, Giles, & Storm, Laura (2019). Regenerative Leadership: The DNA of Life-Affirming 21st Century Organizations. CFM Media. ISBN: 9781783241194.'
		},
		{
			id: 'doughnut-economics',
			title: 'Doughnut economics',
			author: 'Kate Raworth',
			link: 'https://www.saxo.com/dk/doughnut-economics-seven-ways-to-think-like-a-21st-century-economist-pb-b-format_paperback_9781847941398?srsltid=AU7gw4WNqUOvOxQOT6E9Cgs9YWFY7L7y7I4CPGx7Awz11UULEPPeA_Z-',
			image: 'https://imgcdn.saxo.com/_9781847941398',
			alt: 'Raworth, Kate (2018). Doughnut Economics: Seven Ways to Think Like a 21st-Century Economist. Random House Business Books. ISBN: 9781847941398.'
		},
		{
			id: 'nok',
			title: 'Nok',
			author: 'Toke Haunstrup',
			link: 'https://www.saxo.com/dk/nok_bog_9788797628607?srsltid=AU7gw4VrcT_NmDNQAEyUvyamqGJj11OVOApXceIgjmaRKnOvAOjM3fNL',
			image: 'https://imgcdn.saxo.com/_9788797628607',
			alt: 'Haunstrup, Toke (2025). Nok: Fra overflod til trivsel. Forlaget Satis. ISBN: 9788797628607.'
		},
		{
			id: 'underskud',
			title: 'Underskud',
			author: 'Emma Holten',
			link: 'https://www.saxo.com/dk/underskud_bog_9788740074130?srsltid=AU7gw4UvKQkoGobVtD8L6YfckWtBok4iftl5wepJxuQZM2Rg2e1Nnffd',
			image: 'https://imgcdn.saxo.com/_9788740074130',
			alt: 'Holten, Emma (2024). Underskud: Om værdien af omsorg. Politikens Forlag. ISBN: 9788740074130.'
		},
		{
			id: 'coming-home-to-who-you-are',
			title: 'Coming Home to Who you Are - Education Reenlightened',
			author: 'Mark Vandeneijnde & M. Aurelius Higgs',
			link: 'https://www.amazon.com/Coming-Home-Who-You-ReEnlightened/dp/B0DYNQ1KVP',
			image: 'https://m.media-amazon.com/images/I/71SS3cQY-ZL._SY466_.jpg',
			alt: 'Higgs, M. Aurelius, & Vandeneijnde, Mark (2025). Coming Home to Who You Are: Education ReEnlightened (Monia Pereira, illustrator). Independently published. ISBN: 9798333170613.'
		},
		{
			id: 'theory-u',
			title: 'Theory U',
			author: 'Otto Scharmer',
			link: 'https://www.saxo.com/dk/theory-u-leading-from-the-future-as-it-emerges_c-otto-scharmer_hardback_9781626567986?srsltid=AU7gw4XUTtrxNmVromaIR8Tlh-1Blun7aoDREghU7HRXwOfgaJowri1k',
			image: 'https://imgcdn.saxo.com/_9781626567986',
			alt: 'Scharmer, C. Otto (2016). Theory U: Leading from the Future as It Emerges (2nd ed.). Berrett-Koehler Publishers. ISBN: 9781626567986.'
		},
		{
			id: 'braiding-sweetgrass',
			title: 'Braiding Sweetgrass',
			author: 'Robin Wall Kimmerer',
			link: 'https://www.amazon.com/Braiding-Sweetgrass-Indigenous-Scientific-Knowledge/dp/1571313567',
			image: 'https://m.media-amazon.com/images/I/71OgjPcg6-L._SY466_.jpg',
			alt: 'Kimmerer, Robin Wall (2015). Braiding Sweetgrass: Indigenous Wisdom, Scientific Knowledge and the Teachings of Plants. Milkweed Editions. ISBN: 9781571313560.'
		},
		{
			id: 'hospicing-modernity',
			title: 'Hospicing Modernity',
			author: 'Vanesa Machado de Oliveira',
			link: 'https://www.northatlanticbooks.com/shop/hospicing-modernity/',
			image: 'https://www.northatlanticbooks.com/wp-content/uploads/books/hospicing-modernity.png',
			alt: "Machado de Oliveira, Vanessa (2021). Hospicing Modernity: Facing Humanity's Wrongs and the Implications for Social Activism. North Atlantic Books. ISBN: 9781623176242."
		},
		{
			id: 'the-art-of-regenerative-educatorship',
			title: 'The Art of Regenerative Educatorship',
			author: 'Mieke Lopes Cardozo, Koen Wessels, Bas van den Berg',
			link: 'https://www.routledge.com/The-Art-of-Regenerative-Educatorship-A-Developmental-Guide/LopesCardozo-Wessels-Berg/p/book/9789048570522',
			image: 'https://images.routledge.com/common/jackets/crclarge/978904857/9789048570522.jpg',
			alt: 'Lopes Cardozo, Mieke, Wessels, Koen, & van den Berg, Bas (Eds.) (2025). The Art of Regenerative Educatorship: A Developmental Guide. Routledge. ISBN: 9789048570522.'
		},
		{
			id: 'learning-as-if-life-depended-on-it',
			title: 'Learning as if Life Depended on It',
			author: 'Olli-Pekka Heinonen',
			link: 'https://www.penguinrandomhouse.com/books/821963/learning-as-if-life-depended-on-it-by-olli-pekka-heinonen/',
			image: 'https://images3.penguinrandomhouse.com/cover/9781914568077',
			alt: 'Heinonen, Olli-Pekka (2025). Learning as if Life Depended on It: Why We Must See the World Anew, and Figure Out What Follows. Perspectiva. ISBN: 9781914568077.'
		}
	];
	// const hideBookModals = $state(providedBooks.map((book) => ({ id: book.id, hidden: false })));
	let visibleModule = $state('');
	let bookInModal = $derived(providedBooks.find((book) => book.id === visibleModule));
	let comment = $state('');
	let sharerName = $state('');
	let parsedBookComments = $derived(
		booksAnswersSorted.flatMap((answer) => {
			try {
				const content: { bookdid?: unknown; comment?: unknown } | null = JSON.parse(answer.content);
				return typeof content?.bookdid === 'string' && typeof content.comment === 'string'
					? [{ ...answer, bookId: content.bookdid, content: content.comment }]
					: [];
			} catch {
				return [];
			}
		})
	);
	let bookComments = $derived(
		parsedBookComments.filter((answer) => answer.bookId === bookInModal?.id)
	);
	let commentCounts = $derived.by(() => {
		const counts = new Map<string, number>();
		for (const answer of parsedBookComments) {
			counts.set(answer.bookId, (counts.get(answer.bookId) ?? 0) + 1);
		}
		return counts;
	});

	const submitComment = () => {
		const pending = socketio?.pendingEntities[0];
		if (!socketio || !pending || !bookInModal || !comment.trim()) return;

		pending.content = JSON.stringify({ bookdid: bookInModal.id, comment });
		pending.confidential = sharerName.trim() || 'Anonymous';
		socketio.addPendingAccessPolicy(pending.id, {
			public: true,
			action: Action.READ
		});
		socketio.submitEntity(pending, questionid, true);
		socketio.createPending();
		comment = '';
	};
</script>

<div
	class="grid h-full w-full grid-cols-5 items-center justify-center justify-items-center gap-x-6 gap-y-10 overflow-auto p-10"
>
	{#each providedBooks as book, index (index)}
		<Book {book} commentCount={commentCounts.get(book.id) ?? 0} bind:showModal={visibleModule} />
	{/each}
	<!-- <button
		class="btn btn-secondary-container shadow-base-shadow flex h-90 w-65 items-center justify-center rounded-3xl align-middle shadow-lg"
	>
		<Icon icon="akar-icons:plus" class="size-30" />
	</button> -->
</div>

<div
	class="fixed top-1/2 left-1/2 z-50 max-h-4/5 w-3/4 -translate-x-1/2 -translate-y-1/2 overflow-y-auto"
>
	<CardOverlay
		class="bg-primary-container text-primary-container-content  rounded-3xl"
		bind:hidden={
			() => visibleModule === '',
			(hidden) => {
				if (hidden) visibleModule = '';
			}
		}
	>
		{#snippet header()}
			<div class="text-5xl font-bold">{bookInModal?.title}</div>
		{/snippet}
		<!-- {#if bookInModal} -->
		<dl class="text-left text-3xl">
			<dt class="inline-flex items-center gap-2 whitespace-nowrap">
				<Icon icon="fa-solid:pen-fancy" />Author:
			</dt>
			<dd>{bookInModal?.author}</dd>
		</dl>
		<dl class="text-left text-3xl">
			<dt class="inline-flex items-center gap-2 whitespace-nowrap">
				<Icon icon="akar-icons:link-chain" />Source:
			</dt>
			<dd>
				<a
					class="link link-animated break-all whitespace-normal"
					href={bookInModal?.link}
					target="_blank"
					rel="noopener noreferrer">{bookInModal?.link}</a
				>
			</dd>
		</dl>
		<dl class="text-left text-3xl">
			<dt class="inline-flex items-center gap-2 whitespace-nowrap">
				<Icon icon="si:quote-line" /> Reference:
			</dt>
			<dd>{bookInModal?.alt}</dd>
		</dl>
		<dl class="text-left text-3xl">
			<dt class="inline-flex items-center gap-2 whitespace-nowrap">
				<Icon icon="fa7-regular:comments" /> Comments:
			</dt>
			<dd>
				{#snippet messageAnswer(name: string, text: string, date: Date | undefined, index: number)}
					<div class="chat chat-receiver w-full">
						<div
							class="chat-bubble w-[90%]! max-w-none! text-left text-3xl text-wrap break-words {index %
							2
								? 'chat-bubble-accent'
								: 'chat-bubble-primary'}"
						>
							<dl>
								<dt class="italic">{name}:</dt>
								<dd>{text}</dd>
							</dl>
							<div class="label text-right">
								{date
									? new Date(date).toLocaleString(undefined, {
											dateStyle: 'short',
											timeStyle: 'short'
										})
									: 'Thanks for your contribution 🙏'}
							</div>
						</div>
					</div>
				{/snippet}
				<div class="max-h-[600px] w-full overflow-y-auto">
					{#each bookComments as answer, index (answer.id)}
						<div animate:flip={{ duration: 300 }}>
							{@render messageAnswer(
								answer.confidential || 'Anonymous',
								answer.content,
								answer.creation_date,
								index
							)}
						</div>
					{/each}
				</div>
				<div class="text-left">
					{#if socketio?.pendingEntities[0]}
						<div
							class="mt-4 grid w-[90%]! grid-cols-[max-content_minmax(0,1fr)] items-center gap-4 md:grid-cols-[max-content_minmax(0,8rem)_minmax(0,1fr)]"
						>
							<label class="text-3xl whitespace-nowrap" for="sharer_name"> Your Name: </label>
							<input
								type="text"
								placeholder="Name"
								id="sharer_name"
								class="input input-md bg-secondary-container text-secondary-container-content w-full min-w-0 rounded-xl border placeholder:text-2xl placeholder:italic"
								name="name"
								bind:value={sharerName}
							/>
							<label class="col-span-2 min-w-0 text-3xl md:col-span-1" for="sharing">
								📖 What's your take on this book?
							</label>
							<textarea
								class="bg-secondary-container text-secondary-container-content col-span-3 w-full resize-none rounded-2xl border p-2 text-2xl shadow-inner placeholder:text-2xl placeholder:italic"
								placeholder="Please type here - sharing is caring 🫶 - Press Enter to send."
								id="sharing"
								required
								bind:value={comment}
								onkeydown={(event) => {
									if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
										event.preventDefault();
										submitComment();
									}
								}}></textarea>
						</div>
					{:else}
						<div class="label text-error">
							<span class="icon-[svg-spinners--12-dots-scale-rotate] size-6"></span>connecting ...
						</div>
					{/if}
				</div>
			</dd>
		</dl>

		<!-- {/if} -->
	</CardOverlay>
</div>

<div class="col-span-12 mr-20 text-right text-xl">
	By entering your text here, you agree to the <a
		href="#terms-and-conditions"
		class="link link-animated">terms and conditions</a
	>.
</div>
