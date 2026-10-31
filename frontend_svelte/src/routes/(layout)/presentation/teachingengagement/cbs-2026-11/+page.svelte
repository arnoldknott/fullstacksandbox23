<script lang="ts">
	import Icon from '@iconify/svelte';
	import QRCode from 'qrcode';
	import type { RevealApi } from 'reveal.js';
	import { getContext, onDestroy, onMount } from 'svelte';

	import { page } from '$app/state';
	import RevealJs, { toggleOnFragment } from '$components/RevealJS.svelte';
	import { SocketIO } from '$lib/socketio.svelte';
	import { FSSB23_THEME_KEY, type ThemeRuntimeContext } from '$lib/theming';
	import type { MessageExtended, QuestionExtended } from '$lib/types';

	import DataList from '../DataList.svelte';
	import type { PageData } from './$types';
	import CardOverlay from './CardOverlay.svelte';
	import ChatBubble from './ChatBubble.svelte';
	import Comments from './Comments.svelte';
	import DivergingStackedChart from './DivergingStackedChart.svelte';
	import FramedSlide from './FramedSlide.svelte';
	import { getInputsUrl } from './inputs';
	import Library from './Library.svelte';
	import MapAnnotation from './MapAnnotation.svelte';
	import MotivationTable from './MotivationTable.svelte';
	import NameCloud from './NameCloud.svelte';
	import Overview from './Overview.svelte';
	import PresenterControls from './PresenterControls.svelte';
	import QrCode from './QrCode.svelte';
	// import QualitativeFeedback from './QualitativeFeedback.svelte';
	import TermsAndConditions from './TermsAndConditions.svelte';

	let { data }: { data: PageData } = $props();

	let presenterMode = $derived(page.url.searchParams.get('presenter') === 'true');
	let revealInstance = $state<RevealApi | undefined>(undefined);
	let namesQuestion = $derived(
		data.payload.questions.find((question) => question.question === 'cbs-names')
	);

	let placesQuestion = $derived(
		data.payload.questions.find((question) => question.question === 'cbs-places')
	);
	let booksQuestion = $derived(
		data.payload.questions.find((question) => question.question === 'cbs-books')
	);
	let commentsQuestion = $derived(
		data.payload.questions.find((question) => question.question === 'cbs-comments')
	);
	let socketioNames: SocketIO<MessageExtended> = $state()!;
	let socketioPlaces: SocketIO<MessageExtended> = $state()!;
	let socketioBooks: SocketIO<MessageExtended> = $state()!;
	let socketioComments: SocketIO<MessageExtended> = $state()!;
	let socketioPresenterState = $state<SocketIO<QuestionExtended>>();

	onMount(() => {
		if (data.payload.presenterStateSnapshot.entities.length) {
			socketioPresenterState = new SocketIO<QuestionExtended>(
				{
					namespace: '/question',
					sessionId: page.data.session?.sessionId,
					queryParams: { 'request-access-data': true }
				},
				{ snapshot: data.payload.presenterStateSnapshot }
			);
		}
		// socketioMotivation = new SocketIO<NumericalExtended>(
		// 	{
		// 		namespace: '/numerical',
		// 		parentId: motivationQuestion?.id
		// 	},
		// 	{
		// 		snapshot: data.payload.motivationSnapshot
		// 	}
		// );
		socketioNames = new SocketIO<MessageExtended>(
			{
				namespace: '/message',
				parentId: namesQuestion?.id,
				queryParams: { 'request-access-data': true }
			},
			{
				snapshot: data.payload.namesSnapshot,
				template: {
					content: JSON.stringify({
						emoji: '📍',
						text: '',
						coords: { lat: 0, lng: 0 }
					}),
					language: 'en'
				}
			}
		);
		socketioPlaces = new SocketIO<MessageExtended>(
			{
				namespace: '/message',
				parentId: placesQuestion?.id,
				queryParams: { 'request-access-data': true }
			},
			{
				snapshot: data.payload.placesSnapshot,
				template: {
					content: JSON.stringify({
						emoji: '📍',
						text: '',
						coords: { lat: 0, lng: 0 }
					}),
					language: 'en'
				}
			}
		);
		socketioPlaces.createSortedSelection('sortedPlacesAnswers', 'creation_date', false);
		socketioBooks = new SocketIO<MessageExtended>(
			{
				namespace: '/message',
				parentId: booksQuestion?.id,
				queryParams: { 'request-access-data': true }
			},
			{
				snapshot: data.payload.booksSnapshot,
				template: { content: '', language: 'en' }
			}
		);
		socketioBooks.createSortedSelection('sortedBooksAnswers', 'creation_date', false);
		socketioComments = new SocketIO<MessageExtended>(
			{
				namespace: '/message',
				parentId: commentsQuestion?.id,
				queryParams: { 'request-access-data': true }
			},
			{
				snapshot: data.payload.commentsSnapshot,
				template: { content: '', language: 'en' }
			}
		);
		socketioComments.createSortedSelection('sortedCommentsAnswers', 'creation_date', false);
	});

	onDestroy(() => {
		socketioPresenterState?.client.disconnect();
		// socketioMotivation?.client.disconnect();
		socketioPlaces?.client.disconnect();
		socketioNames?.client.disconnect();
		socketioBooks?.client.disconnect();
		socketioComments?.client.disconnect();
	});

	const themeRuntime = getContext<ThemeRuntimeContext>(FSSB23_THEME_KEY);

	let businessCaseImage: HTMLImageElement | undefined = $state();

	let qrCodeModalsHidden: Record<string, boolean> = $state({
		names: true,
		map: true, // TBD: change to false after developing
		books: true,
		comments: true
	});

	let returnToSlide = $state<string | undefined>(undefined);
	$effect(() => {
		const handleSlideChanged = (event: Event) => {
			const { currentSlide, previousSlide } = event as Event & {
				currentSlide?: HTMLElement;
				previousSlide?: HTMLElement;
			};
			if (currentSlide?.id === 'terms-and-conditions' && previousSlide?.id) {
				returnToSlide = previousSlide.id;
			}
		};
		revealInstance?.on('slidechanged', (event: Event) => handleSlideChanged(event));
		return () => revealInstance?.off('slidechanged', handleSlideChanged);
	});

	let modulesContentColumn: HTMLDivElement | undefined = $state();

	let aboutMe = $state({
		studies: true,
		industry: true,
		phd: true,
		research: true,
		sabbatical: true,
		teaching: true
	});
	let showExplodingHead = $state(false);

	let outerChange = $state({
		reflections: true,
		closedQuestions: true,
		openQuestions: true
	});

	const hideAllToggleOne = <K extends string>(toggleKey: K, list: Record<K, boolean>): void => {
		for (const key in list) {
			list[key] = key === toggleKey ? !list[key] : true;
		}
	};
	const toggleAboutMe = (buttonText: string) => {
		if (!aboutMe.research) showExplodingHead = true;
		hideAllToggleOne(buttonText.replaceAll('.', '').toLowerCase(), aboutMe);
	};
	const setResearchOverlayHidden = (hidden: boolean) => {
		if (hidden && !aboutMe.research) showExplodingHead = true;
		aboutMe.research = hidden;
	};

	let circularItems: Record<string, HTMLDivElement | undefined> = $state({});
	let connectorLines: Record<string, HTMLDivElement | undefined> = $state({});
	type NoExamEntry = {
		year: number;
		course?: string;
		learnedMore: number[];
		takeMoreResponsibility: number[];
		moreMotivated: number[];
		meditation?: number[];
	};

	const categoriesNoExam: [string, string, string, string, string] = [
		'totally disagree',
		'disagree',
		'same',
		'agree',
		'fully agree'
	];

	const noExamData: NoExamEntry[] = [
		{
			year: 2024,
			course: 'Master',
			learnedMore: [4, 9, 33, 11, 9],
			takeMoreResponsibility: [1, 7, 13, 28, 17],
			moreMotivated: [4, 15, 16, 18, 13]
		},
		{
			year: 2025,
			course: '2nd semester',
			learnedMore: [5, 29, 45, 22, 8],
			takeMoreResponsibility: [3, 23, 37, 30, 15],
			moreMotivated: [7, 28, 37, 23, 14]
		},
		{
			year: 2025,
			course: '4th semester',
			learnedMore: [7, 37, 58, 26, 9],
			takeMoreResponsibility: [6, 24, 34, 52, 21],
			moreMotivated: [7, 31, 46, 38, 14]
		},
		{
			year: 2025,
			course: 'Master',
			learnedMore: [1, 6, 28, 13, 9],
			takeMoreResponsibility: [1, 4, 17, 22, 13],
			moreMotivated: [2, 10, 18, 19, 8],
			meditation: [18, 0, 31] // from mentimeter - maybe was not an option here!
		},
		{
			year: 2026,
			course: '2nd semester', // includes 34603.
			learnedMore: [7, 22, 41, 21, 12],
			takeMoreResponsibility: [4, 20, 34, 28, 17],
			moreMotivated: [7, 22, 25, 29, 18],
			meditation: [25, 41, 57]
		},
		{
			year: 2026,
			course: '4th semester',
			learnedMore: [2, 16, 41, 30, 4],
			takeMoreResponsibility: [1, 16, 26, 42, 7],
			moreMotivated: [2, 23, 33, 23, 11],
			meditation: [28, 24, 46]
		},
		{
			year: 2026,
			course: 'Master',
			learnedMore: [],
			takeMoreResponsibility: [],
			moreMotivated: [],
			meditation: [8, 9, 23]
		}
	];

	const meditationData = noExamData.map((entry) => ({
		year: entry.year,
		course: entry.course,
		values: entry.meditation ?? []
	}));

	const learnedMoreData = noExamData.map((entry) => ({
		year: entry.year,
		course: entry.course,
		values: entry.learnedMore
	}));

	const moreResponsibilityData = noExamData.map((entry) => ({
		year: entry.year,
		course: entry.course,
		values: entry.takeMoreResponsibility
	}));

	const moreMotivatedData = noExamData.map((entry) => ({
		year: entry.year,
		course: entry.course,
		values: entry.moreMotivated
	}));

	const qrCodeEmailPromise = $derived(
		QRCode.toDataURL(
			`mailto:knott@dtu.dk?subject=${encodeURIComponent(`Follow-up on CBS Library event, November 2nd 2026`)}`
		)
	);
</script>

{#snippet interactiveElementNotAvailable(elementName: string)}
	<div class="flex h-full w-full flex-col items-center justify-center gap-5 text-center">
		<div class="text-6xl font-bold">⚠️</div>
		<div class="text-2xl font-semibold">Interactive {elementName} is not available.</div>
		<div class="text-base-content/70 text-lg">
			This interactive element is not available in the current context.<br />
			Please inform the presenter about it.
		</div>
	</div>
{/snippet}

{#snippet timeLineRow(from: string, to: string, icons: string[], buttonText: string, text: string)}
	<div class="label self-center align-middle text-5xl">{from}</div>
	<div class="label self-center text-5xl">-</div>
	<div class="label self-center text-5xl">{to}</div>
	<div class="flex justify-center gap-2 self-center">
		{#each icons as icon, idx (icon)}
			<Icon icon="emojione-v1:flag-for-{icon}" class="inline-block size-10" />
			{#if idx < icons.length - 1}
				<Icon icon="streamline:ampersand-solid" class="inline-block size-6 self-center" />
			{/if}
		{/each}
	</div>
	<button
		class="btn btn-xl btn-gradient btn-secondary-container shadow-base-shadow rounded-full text-5xl font-semibold shadow"
		onclick={() => toggleAboutMe(buttonText)}
	>
		{buttonText}
	</button>
	<div class="label self-center text-left text-5xl">
		{text}
	</div>
{/snippet}

<RevealJs bind:reveal={revealInstance} options={{ hash: true, fragmentInURL: true }}>
	<FramedSlide part="welcome" hideProgressBar>
		<div
			class="text-base-content-variant flex h-full items-center justify-center text-[200px] font-bold"
		>
			Welcome
		</div>
		{#each socketioNames?.entities as entity (entity.id)}
			{#if entity.confidential}
				<NameCloud text={entity.confidential} />
			{/if}
		{/each}
		{#snippet footerRight()}
			{#if presenterMode}
				<PresenterControls {revealInstance} socketio={socketioPresenterState} />
			{/if}
		{/snippet}
		<!-- <div class="absolute right-0 bottom-0 z-50 flex items-center gap-2 p-4">
			<PresenterControls {revealInstance} socketio={socketioPresenterState} />
		</div> -->
		<!-- {#if namesQuestion}
			<div class="mt-8 flex justify-start">
				<QrCode url={getInputsUrl(page.url, 'cbs-names')} bind:modalHidden={qrCodeModalsHidden.names} />
			</div>
		{/if} -->
	</FramedSlide>
	<!-- <section id="welcome" class="h-full">
		<div
			class="text-base-content-variant flex h-full items-center justify-center text-[200px] font-bold"
		>
			Welcome
		</div>
		<div class="absolute right-0 bottom-0 z-50 flex items-center gap-2 p-4">
			<PresenterControls {revealInstance} socketio={socketioPresenterState} />
		</div> -->
	<!-- {#if namesQuestion}
			<div class="mt-8 flex justify-start">
				<QrCode url={getInputsUrl(page.url, 'cbs-names')} bind:modalHidden={qrCodeModalsHidden.names} />
			</div>
		{/if} -->
	<!-- </section> -->
	<FramedSlide part="overview" hideProgressBar={true}>
		<Overview
			items={[
				// {
				// 	icon: 'fluent-emoji-flat:construction',
				// 	title: 'TBD: think of new structure!'
				// }
				{
					icon: 'stash:circle-dot',
					title: 'Context'
				},
				// // {
				// // 	icon: 'vaadin:thumbs-up-o',
				// // 	title: 'Motivation'
				// // },
				// {
				// 	icon: 'game-icons:ancient-ruins',
				// 	title: 'Before'
				// },
				{
					icon: 'glyphs:books-bold',
					title: 'Inspiration'
				},
				{
					icon: 'carbon:development',
					title: 'Implementation'
				},
				{
					icon: 'bi:bar-chart',
					title: 'Results'
				}
				// {
				// 	icon: 'ci:star',
				// 	title: 'Present Moment'
				// },
			]}
		/>
		<!-- <div class="absolute top-0 right-0 h-[100px] w-[800px]">
			<div class="h-full w-full border-4 border-red-400">progress</div>
		</div> -->
	</FramedSlide>
	<FramedSlide part="context" title="About me">
		<div
			class="mx-10 grid grid-cols-[minmax(0,1fr)_10px_minmax(0,1fr)_120px_270px_minmax(0,8fr)] gap-8 gap-y-12"
		>
			{@render timeLineRow('2000', '2004', ['germany'], 'Studies', 'Electrical Engineering')}
			{@render timeLineRow(
				'2004',
				'2009',
				['germany', 'united-states'],
				'Industry',
				'Automotive Sound Systems'
			)}
			{@render timeLineRow(
				'2007',
				'2010',
				['denmark', 'germany'],
				'Ph.D.',
				'Power Electronics at DTU'
			)}
			{@render timeLineRow('2010', '2018', ['denmark'], 'Research', 'Miniaturising Power Supplies')}
			{#if showExplodingHead}
				<Icon
					icon="fluent-emoji-flat:exploding-head"
					class="col-span-full justify-self-center text-7xl"
				/>
				{@render timeLineRow('2018', '2018', ['white-flag'], 'Sabbatical', 'Dirtbacking')}
			{/if}
			{@render timeLineRow('2019', '2026', ['denmark'], 'Teaching', 'Focus on Teaching')}
		</div>
		<CardOverlay
			class="bg-base-250 text-base-content absolute top-1/2 left-1/2 z-50 w-fit -translate-x-1/2 -translate-y-1/2 pt-6 text-4xl"
			bind:hidden={aboutMe.studies}
		>
			{#snippet header()}
				<div class="text-5xl font-bold">Studies</div>
			{/snippet}
			<dl class="text-5xl">
				<dt class="mb-4 font-bold text-nowrap">
					<Icon icon="fluent-emoji-flat:school" class="mr-2 inline-block" /> Diplom engineer for Electrical
					Engineering
				</dt>
				<dd class="mb-4 pl-4">General Electronics and</dd>
				<dd class="mb-4 pl-4">Semiconductor Electronics</dd>
				<dd class="mb-4 pl-4">
					<a href="https://www.th-deg.de/" class="link link-animated" target="_blank"
						>Deggendorf Institute of Technology</a
					>
				</dd>
			</dl>
		</CardOverlay>
		<CardOverlay
			class="bg-base-250 text-base-content absolute top-1/2 left-1/2 z-50 w-fit -translate-x-1/2 -translate-y-1/2 pt-6 text-4xl"
			bind:hidden={aboutMe.industry}
		>
			{#snippet header()}
				<div class="text-7xl font-bold">Industry</div>
			{/snippet}
			<dl class="text-5xl">
				<dt class="mb-4 font-bold text-nowrap">
					<Icon icon="emojione-v1:flag-for-germany" class="mr-2 inline-block" /> Harman/Becker Automotive
					Systems GmbH
				</dt>
				<dd class="mb-4 pl-4">(now Samsung)</dd>
				<dd class="mb-4 pl-4">research and pre-development</dd>
				<dd class="mb-4 pl-4">for automotive sound systems</dd>
			</dl>
			<dl class="text-5xl">
				<dt class="mt-5 mb-4 font-bold text-nowrap">
					<Icon icon="emojione-v1:flag-for-united-states" class="mr-2 inline-block" /> At sister company
					in USA
				</dt>
				<dd class="mb-4 pl-4">for 1.5 years</dd>
			</dl>
			<!-- <dl
				class="bg-warning-container text-warning-container-content shadow-base-shadow rounded-2xl text-5xl shadow"
			>
				<dt class="mt-5 mb-4 font-bold text-nowrap">
					<Icon icon="fluent-color:warning-28" class="mr-2 inline-block" /> Fun job
				</dt>
				<dd class="mb-4 pl-4">worked many hours a week</dd>
			</dl> -->
		</CardOverlay>
		<CardOverlay
			class="bg-base-250 text-base-content absolute top-1/2 left-1/2 z-50 w-fit -translate-x-1/2 -translate-y-1/2 pt-6 text-4xl"
			bind:hidden={aboutMe.phd}
		>
			{#snippet header()}
				<div class="text-5xl font-bold">Ph.d. student</div>
			{/snippet}
			<dl class="text-5xl">
				<dt class="mb-4 font-bold text-nowrap">
					<Icon icon="emojione-v1:flag-for-denmark" class="mr-2 inline-block" /> Technical University
					of Denmark (DTU)
				</dt>
				<dd class="mb-4 pl-4">Power Electronics and Sound Systems</dd>
				<dd class="mb-4 pl-4">Highly energy efficient electronics</dd>
				<!-- <dd class="mb-4 pl-4">Amplifiers</dd> -->
			</dl>
			<dl class="text-5xl">
				<dt class="mt-5 mb-4 font-bold text-nowrap">
					<Icon icon="emojione-v1:flag-for-germany" class="mr-2 inline-block" /> overlap with industry
					job
				</dt>
			</dl>
			<!-- <dl class="text-5xl">
				<dt class="mt-5 mb-4 font-bold text-nowrap">
					<Icon icon="fluent-emoji-flat:glowing-star" class="mr-2 inline-block" /> Hobbies
				</dt>
				<dd class="mb-4 pl-4">Learning Danish</dd>
			</dl> -->
			<dl class="text-5xl">
				<dt class="mt-5 mb-4 font-bold text-nowrap">
					<Icon icon="emojione:rocket" class="mr-2 inline-block" /> Venture Cup
				</dt>
				<dd class="mb-4 pl-4">good time at CBS!</dd>
				<dd class="mb-4 pl-4">won a prize</dd>
			</dl>
			<!-- <dl
				class="bg-warning-container text-warning-container-content shadow-base-shadow rounded-2xl text-5xl shadow"
			>
				<dt class="mt-5 mb-4 font-bold text-nowrap">
					<Icon icon="fluent-color:warning-28" class="mr-2 inline-block" /> Two part time contracts
				</dt>
				<dd class="mb-4 pl-4">Two times 3/4 of full time</dd>
			</dl> -->
		</CardOverlay>
		<CardOverlay
			class="bg-base-250 text-base-content absolute top-1/2 left-1/2 z-50 w-fit -translate-x-1/2 -translate-y-1/2 pt-6 text-4xl"
			bind:hidden={() => aboutMe.research, (hidden) => setResearchOverlayHidden(hidden)}
		>
			{#snippet header()}
				<div class="text-5xl font-bold">Focus on Research</div>
			{/snippet}
			<dl class="text-5xl">
				<dt class="mb-4 font-bold text-nowrap">
					<Icon icon="fluent-emoji-flat:green-heart" class="mr-2 inline-block" /> Intention
				</dt>
				<dd class="mb-4 pl-4">using less material to provide same energy</dd>
			</dl>
			<dl class="text-5xl">
				<dt class="mt-5 mb-4 font-bold text-nowrap">
					<Icon icon="fluent-color:lightbulb-32" class="mr-2 inline-block" /> Research & Teaching
				</dt>
				<dd class="mb-4 pl-4">3 research projects with industry</dd>
				<dd class="mb-4 pl-4">4 start-up companies</dd>
				<dd class="mb-4 pl-4">2 courses</dd>
			</dl>
			<!-- <dl
				class="bg-warning-container text-warning-container-content shadow-base-shadow rounded-2xl text-5xl shadow"
			>
				<dt class="mt-5 mb-4 font-bold text-nowrap">
					<Icon icon="fluent-color:warning-28" class="mr-2 inline-block" /> Meetings / Courses / Supervision
				</dt>
			</dl> -->
		</CardOverlay>
		<!-- TBD: make it a bang here? -->
		<CardOverlay
			class="bg-base-250 text-base-content absolute top-1/2 left-1/2 z-50 w-fit -translate-x-1/2 -translate-y-1/2 pt-6 text-4xl"
			bind:hidden={aboutMe.sabbatical}
		>
			{#snippet header()}
				<div class="text-5xl font-bold">Sabatical</div>
			{/snippet}
			<dl class="text-5xl">
				<dt class="mb-4 font-bold text-nowrap">
					<Icon icon="noto:hiking-boot" class="mr-2 inline-block" /> Being nature
				</dt>
				<dd class="mb-4 pl-4">5.5 months in nature</dd>
				<dd class="mb-4 pl-4">Hiking and outdoor activities</dd>
				<!-- <dd class="mb-4 pl-4">Amplifiers</dd> -->
			</dl>
			<!-- <dl
				class="bg-success-container text-success-container-content shadow-base-shadow rounded-2xl text-5xl shadow"
			>
				<dt class="mt-5 mb-4 font-bold text-nowrap">
					<Icon icon="fluent-color:checkmark-circle-32" class="mr-2 inline-block" /> Batteries refilled
				</dt>
			</dl> -->
		</CardOverlay>
		<CardOverlay
			class="bg-base-250 text-base-content absolute top-1/2 left-1/2 z-50 w-fit -translate-x-1/2 -translate-y-1/2 pt-6 text-4xl"
			bind:hidden={aboutMe.teaching}
		>
			{#snippet header()}
				<div class="text-5xl font-bold">Teaching</div>
			{/snippet}
			<dl class="text-5xl">
				<dt class="mb-4 font-bold text-nowrap">
					<Icon icon="fluent-emoji-flat:teacher-medium" class="mr-2 inline-block" /> 3 courses
				</dt>
				<dd class="mb-4 pl-4">2nd semester mandatory B.Sc.</dd>
				<dd class="mb-4 pl-4">4th semester elective B.Sc</dd>
				<dd class="mb-4 pl-4">Master course</dd>
				<dd class="mb-4 pl-4">in total 300 students per year</dd>
				<!-- <dd class="mb-4 pl-4">Amplifiers</dd> -->
			</dl>
			<dl class="text-5xl">
				<dt class="mb-4 font-bold text-nowrap">
					<Icon icon="streamline-stickies-color:programming" class="mr-2 inline-block" /> Programming
				</dt>
				<dd class="mb-4 pl-4">For example this presentation</dd>
			</dl>
			<!-- <dl
				class="bg-success-container text-success-container-content shadow-base-shadow rounded-2xl text-5xl shadow"
			>
				<dt class="mt-5 mb-4 font-bold text-nowrap">
					<Icon icon="fluent-color:checkmark-circle-32" class="mr-2 inline-block" /> Working as hard as
					20 years ago
				</dt>
				<dd class="mb-4 pl-4">and taking really good care of myself</dd>
			</dl> -->
		</CardOverlay>
	</FramedSlide>
	<FramedSlide part="context" section="map" hideProgressBar title="About you?">
		{#if placesQuestion}
			<!-- <div class="text-secondary text-center text-7xl font-bold">Check in</div> -->
			<MapAnnotation {revealInstance} socketio={socketioPlaces} />
		{:else}
			{@render interactiveElementNotAvailable('map')}
		{/if}
		{#snippet footerLeft()}
			{#if placesQuestion && presenterMode}
				<QrCode
					url={getInputsUrl(page.url, 'cbs-places')}
					bind:modalHidden={qrCodeModalsHidden.map}
				/>
				<!-- <button
					class="btn btn-info-container btn-gradient label btn shadow-outline relative z-[1000] mx-4 h-20 w-20 rounded-full shadow-sm"
					aria-label="QR Code"
					onclick={() => (qrCodeModalsHidden.map = !qrCodeModalsHidden.map)}
				>
					<Icon icon="bi:qr-code" class="size-8" />
				</button>
				<div
					class="fixed top-1/2 left-1/2 z-[1000] h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2"
				>
					<CardOverlay
						class="bg-info-container text-info-container-content h-full rounded-2xl"
						bind:hidden={
							() => qrCodeModalsHidden.map,
							(hidden) => {
								if (hidden) qrCodeModalsHidden.map = true;
							}
						}>QR Code here</CardOverlay
					>
				</div> -->
			{/if}
		{/snippet}
	</FramedSlide>
	<section>
		<FramedSlide part="context" section="courses" title="Courses">
			<div class="flex h-full flex-col justify-around gap-4">
				<div
					class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-5 shadow-inner"
				>
					<div class="text-center text-5xl font-bold">2nd semester</div>
					<dl>
						<dt>mandatory course on electrical engineering</dt>
						<dd>core competences</dd>
						<dd>~ 120 students</dd>
						<dd>very pressured semester</dd>
					</dl>
				</div>
				<div
					class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-5 shadow-inner"
				>
					<div class="text-center text-5xl font-bold">4th semester</div>
					<dl>
						<dt>introduction to specialization</dt>
						<dd>hybrid online/presence</dd>
						<dd>~ 100 students</dd>
					</dl>
				</div>
				<div
					class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-5 shadow-inner"
				>
					<div class="text-center text-5xl font-bold">Master level</div>
					<dl>
						<dt>close to applications and product design</dt>
					</dl>
				</div>
			</div>
		</FramedSlide>
		<FramedSlide part="context" section="2nd-semester" title="Course: 2nd semester">
			<div class="grid h-full grid-cols-2 gap-6">
				<div
					class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
				>
					<div class="text-center text-5xl font-bold">Outer Ecosystem</div>
					<ul class="list-disc">
						<li>
							<a
								href="https://kurser.dtu.dk/course/34601"
								class="link link-animated"
								target="_blank"
								rel="noopener noreferrer">Course description</a
							>
						</li>
						<li>core competences in<br />electrical engineering</li>
						<li>mandatory for two study lines</li>
						<li>~ 10 different study lines</li>
						<li>~ 120 participants</li>
						<li>fundamental and mathematical</li>
						<li>intense and challenging content</li>
						<li>
							in parallel with 3 other tough and intense courses: math, physics and programming
						</li>
					</ul>
				</div>
				<div
					class="bg-primary text-primary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
				>
					<div class="text-center text-5xl font-bold">Inner Ecosystem</div>

					<div class="flex justify-between gap-4 py-4">
						<div class="w-full">
							<iframe
								title="Electric circuits slides"
								src="/teachingengagement/presentation-electric-circuits.pdf"
								class="shadow-base-shadow m-0! h-full w-full rounded-4xl object-contain shadow-lg"
							>
							</iframe>
						</div>
						<a
							href="https://www.saxo.com/dk/the-analysis-and-design-of-linear-circuits_bog_9781119913023?srsltid=AU7gw4UBKmyh8Tol04cqWmnOr-5fRqaOctZY3i1baqk6wsAwpZfHKPj2"
							target="_blank"
							rel="noopener noreferrer"
							class="h-full"
						>
							<img
								src="https://imgcdn.saxo.com/_9781119913023"
								alt="The analysis and design of linear circuits - book cover"
								class="shadow-base-shadow mt-0! h-full w-fit rounded-4xl object-contain shadow-lg"
							/>
						</a>
					</div>
					<div class="flex justify-between gap-4 py-4">
						<a
							class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
							href="https://www.youtube.com/@electriccircuitswithaltern7204"
						>
							<Icon icon="fa6-brands:youtube" /> YouTube
						</a>
						<a
							class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
							href="https://chatgpt.com/g/g-69774f07058c8191bd88f547d1c740c9-electric-circuits-with-alternating-currents"
						>
							<Icon icon="bi:openai" /> ChatGPT
						</a>
						<a
							class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
							href="https://gemini.google.com/gem/1j9s5Oe6boPCqdOAGOUMKZmFWr5O6cWuT?usp=sharing"
						>
							<Icon icon="codicon:google-gemini" /> Gemini
						</a>
					</div>
					<ul class="list-disc">
						<li>3 x laboratory group work</li>
						<li>~50 calculation exercises</li>
						<li>~30 knowledge checks (former exam)</li>
					</ul>
				</div>
			</div>
		</FramedSlide>
		<FramedSlide part="context" section="4th-semester" title="Course: 4th semester">
			<div class="grid h-full grid-cols-2 gap-6">
				<div
					class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
				>
					<div class="text-center text-5xl font-bold">Outer Ecosystem</div>
					<ul class="list-disc">
						<li>
							<a
								href="https://kurser.dtu.dk/course/34620"
								class="link link-animated"
								target="_blank"
								rel="noopener noreferrer">Course description</a
							>
						</li>
						<li>introduction to<br />specialisation</li>
						<li>recommended / electable course</li>
						<li>online and physical</li>
						<li>remote participants</li>
						<li>~10 different study lines</li>
						<li>~100 participants</li>
						<li>closes to applications</li>
					</ul>
				</div>
				<div
					class="bg-primary text-primary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
				>
					<div class="text-center text-5xl font-bold">Inner Ecosystem</div>

					<div class="flex justify-between gap-4 py-4">
						<div class="w-full">
							<iframe
								title="Basic Power Electronics slides"
								src="/teachingengagement/presentation-basic-power.pdf"
								class="shadow-base-shadow m-0! h-full w-full rounded-4xl object-contain shadow-lg"
							>
							</iframe>
						</div>
						<a
							href="https://www.amazon.com/Power-Electronics-Course-Ned-Mohan/dp/1118074807"
							target="_blank"
							rel="noopener noreferrer"
							class="h-full"
						>
							<img
								src="https://m.media-amazon.com/images/I/61+7f4Xr0DL._SY425_.jpg"
								alt="Power Electronics: A first course - book cover"
								class="shadow-base-shadow mt-0! h-full w-fit rounded-4xl object-contain shadow-lg"
							/>
						</a>
					</div>
					<div class="flex justify-between gap-4 py-4">
						<a
							class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
							href="https://www.youtube.com/@basicpowerelectronics3928"
						>
							<Icon icon="fa6-brands:youtube" /> YouTube
						</a>
						<a
							class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
							href="https://chatgpt.com/g/g-69776f22b96481918cfa94db0b1e1a7b-basic-power-electronics"
						>
							<Icon icon="bi:openai" /> ChatGPT
						</a>
						<a
							class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
							href="https://gemini.google.com/gem/18nuFlRpN0CqvK7etCPk8mS3qKdFFcfCk?usp=sharing"
						>
							<Icon icon="codicon:google-gemini" /> Gemini
						</a>
					</div>
					<ul class="list-disc">
						<li>6 x laboratory group work</li>
						<li>2 x industry guest lecture</li>
						<li>~30 calculation exercises</li>
						<li>~30 knowledge checks (former exam)</li>
					</ul>
				</div>
			</div>
		</FramedSlide>
		<FramedSlide part="context" section="master-level" title="Course: Master level">
			<div class="grid h-full grid-cols-2 gap-6">
				<div
					class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
				>
					<div class="text-center text-5xl font-bold">Outer Ecosystem</div>
					<ul class="list-disc">
						<li>
							<a
								href="https://kurser.dtu.dk/course/34654"
								class="link link-animated"
								target="_blank"
								rel="noopener noreferrer">Course description</a
							>
						</li>
						<li>electable course</li>
						<li>
							high diversity
							<ul>
								<li>Danish / international</li>
								<li>Bachelor / Master</li>
								<li>Different backgrounds</li>
							</ul>
						</li>
						<li>remote participants</li>
						<li>~12 different study lines</li>
						<li>~100 participants</li>
						<li>close to industrial work experience</li>
					</ul>
				</div>
				<div
					class="bg-primary text-primary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-6 shadow-inner"
				>
					<div class="text-center text-5xl font-bold">Inner Ecosystem</div>
					<div class="flex justify-between gap-4 py-4">
						<a
							class="btn btn-primary-container text-primary-container-content! btn-gradient shadow-base-shadow btn-xl w-[220px] shrink-0 rounded-full text-3xl shadow-lg"
							href="https://www.youtube.com/@circuittechnologyandemc7315"
						>
							<Icon icon="fa6-brands:youtube" /> YouTube
						</a>
					</div>
					<ul class="list-disc">
						<li>3 teachers</li>
						<li>
							methods
							<ul>
								<li>lectures</li>
								<li>flipped classroom</li>
								<li>group work</li>
							</ul>
						</li>
						<li>4 x projects as group work</li>
						<li>4 x industry guest lecture</li>
					</ul>
				</div>
			</div>
		</FramedSlide>
	</section>
	<!-- <section> -->
	<FramedSlide part="context" section="applications" title="Applications">
		<img
			src={`/teachingengagement/${themeRuntime.mode === 'light' ? 'applications-light.png' : 'applications-dark.png'}`}
			alt="Business Case"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
		{#snippet footerRight()}
			<div class="text-right text-xl">
				Picture created by 🤖 <a href="https://chat.openai.com" class="link link-animated"
					>ChatGPT</a
				>
			</div>
		{/snippet}
	</FramedSlide>
	<FramedSlide part="context" section="research" title="Research">
		<img
			bind:this={businessCaseImage}
			src="/teachingengagement/business-case.png"
			alt="Business Case"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
		<div
			class="fragment fade-in bg-primary-container text-primary-container-content shadow-base-shadow absolute top-3/4 left-1/2 flex h-50 w-150 -translate-x-1/2 -translate-y-1/2 transform items-center justify-center rounded-[50%] text-6xl shadow"
			{@attach toggleOnFragment(revealInstance!, businessCaseImage, 'opacity-60')}
		>
			3 industrial<br />
			research projects
		</div>
		<div
			class="fragment fade-in bg-primary-container text-primary-container-content shadow-base-shadow absolute top-1/3 left-3/10 flex h-50 w-120 -translate-x-1/2 -translate-y-1/2 transform items-center justify-center rounded-[50%] text-6xl shadow"
			{@attach toggleOnFragment(revealInstance!, businessCaseImage, 'opacity-60', true)}
			{@attach toggleOnFragment(revealInstance!, businessCaseImage, 'opacity-30')}
		>
			4 start-up<br />
			companies
		</div>
		<div
			class="fragment fade-in"
			{@attach toggleOnFragment(revealInstance!, businessCaseImage, 'opacity-30', true)}
			{@attach toggleOnFragment(revealInstance!, businessCaseImage, 'opacity-10')}
		>
			<Icon
				icon="emojione:cheese-wedge"
				class="absolute top-1/3 left-7/10 size-130 -translate-x-1/2 -translate-y-1/2 transform text-6xl"
			/>
		</div>
	</FramedSlide>
	<FramedSlide part="context" section="rebound" title="Rebound Effect">
		<div class="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] place-items-center gap-8">
			<img
				src={`/teachingengagement/${themeRuntime.mode === 'light' ? 'lightbulb-light.png' : 'lightbulb-dark.png'}`}
				alt="Light Bulb"
				class=" h-fit w-1/2 self-center"
			/>
			<Icon icon="at-icons:arrow-right" class="size-30 self-center" />
			<img
				src={`/teachingengagement/${themeRuntime.mode === 'light' ? 'lightbulb-led-light.png' : 'lightbulb-led-dark.png'}`}
				alt="Light Bulb"
				class=" h-fit w-1/2 self-center"
			/>
			<div class="label text-8xl">💡 50 W</div>
			<Icon icon="at-icons:arrow-down-right" class="text-success size-30 self-center" />
			<div class="label text-8xl">💡 5 W</div>
			<div class="fragment label text-8xl" data-fragment-index="0">🌍 2.8 TWh</div>
			<Icon
				icon="gravity-ui:equal"
				class="fragment text-error size-30 self-center"
				data-fragment-index="0"
			/>
			<div class="fragment label text-8xl" data-fragment-index="0">🌍 ~3 TWh</div>
		</div>
	</FramedSlide>
	<FramedSlide part="context" section="planetary-boundaries" title="Planetary Boundaries">
		<img
			src="https://www.stockholmresilience.org/images/200.1283cdff1a0ad97c666a37/1790600427312/PB_2026.png"
			alt="Planetary Boundaries"
			class="shadow-base-shadow h-fit w-fit self-center rounded-4xl shadow-lg"
		/>
		{#snippet footerRight()}
			<div class="text-right text-xl">
				Source:
				<a
					href="https://www.stockholmresilience.org/research/planetary-boundaries.html"
					class="link link-animated"
				>
					🌐 https://www.stockholmresilience.org
				</a>
			</div>
		{/snippet}
	</FramedSlide>
	<FramedSlide part="context" section="country-overshoot" title="Country Overshoot">
		<img
			src="https://overshoot.footprintnetwork.org/content/uploads/2025/12/GFN-Country-Overshoot-Day-2026_Smallest.jpg"
			alt="Country Overshoot Days"
			class="shadow-base-shadow h-fit w-fit self-center rounded-4xl shadow-lg"
		/>
		{#snippet footerRight()}
			<div class="text-right text-xl">
				Source:
				<a
					href="https://overshoot.footprintnetwork.org/newsroom/country-overshoot-days/"
					class="link link-animated"
				>
					🌐 https://overshoot.footprintnetwork.org/newsroom/country-overshoot-days/
				</a>
			</div>
		{/snippet}
	</FramedSlide>
	<FramedSlide part="context" section="stress" title="Interconnected stress">
		<img
			src="/teachingengagement/stress-interconnection.png"
			alt="Interconnection of Stress"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
		{#snippet footerRight()}
			<div class="text-right text-xl">
				Source:
				<a href="https://www.regenerators.co" class="link link-animated">
					🌐 Regenerators Academy
				</a> by Laura Storm
			</div>
		{/snippet}
	</FramedSlide>
	<!-- </section> -->
	<FramedSlide part="context" section="complexity" title="Complexity">
		<img
			src="https://www.businessillustrator.com/wp-content/uploads/2025/12/complexity-outside-linear-cube-cartoon_businessillustrator.com_1200px-600x314.png.webp"
			alt="Reality strikes back - cartoon"
			class="shadow-base-shadow h-fit w-3/5 self-center rounded-4xl shadow-lg"
		/>
		<iframe
			class="shadow-base-shadow w-3/5 self-center rounded-4xl shadow-lg"
			title="The Story of the Chinese Farmer - Allan Watts"
			data-testid="embed-iframe"
			style="border-radius:12px"
			src="https://open.spotify.com/embed/track/5QTIGUgV4eFrg0o3k8lGTp?utm_source=generator&si=7bc38a38196f43c5"
			width="100%"
			height="80"
			frameBorder="0"
			allowfullscreen={false}
			allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
			loading="lazy"
		></iframe>
		{#snippet footerRight()}
			<div class="text-right text-xl">
				Cartoon by
				<a href="mailto:Virpi@businessillustrator.com" class="link link-animated mt-15">
					📧 Virpi@businessillustrator.com
				</a>,
				<a href="https://www.businessillustrator.com/blog" class="link link-animated">
					🌐 www.businessillustrator.com/blog
				</a>
			</div>
		{/snippet}
	</FramedSlide>
	<FramedSlide part="context" section="change" title="Outer change?">
		<div class="label text-9xl font-bold">
			Who wants <br /> <span class="invisible">to</span> change?
		</div>
		<div
			class="fragment base-content-variant bg-base-300 shadow-base-shadow absolute top-1/10 left-0 m-5 rounded-[50%] p-15 shadow"
		>
			What change <br />do you want to <br />see in the world?
		</div>
		<div
			class="fragment base-content-variant bg-base-300 shadow-base-shadow absolute top-1/10 left-7/10 m-5 rounded-[50%] p-15 shadow"
		>
			What qualities <br />does change reveal<br />in a better world?
		</div>
		<div
			class="fragment base-content-variant bg-base-300 shadow-base-shadow absolute top-6/10 left-0 m-5 rounded-[50%] p-15 shadow"
		>
			How would you like us<br /> to leave the world to<br />the next 1-7 generations?
		</div>
		<div class="fragment absolute top-6/10 left-8/10">
			<Icon icon="emojione-monotone:globe-with-meridians" class="text-success text-[250px]" />
		</div>
		{#snippet footerRight()}
			<div class="text-right text-xl">
				🤔 Inspired by <a
					href="https://www.linkedin.com/in/jacob-rask-b4b805139/"
					class="link link-animated">Jacob Rask</a
				>
			</div>
		{/snippet}
	</FramedSlide>
	<FramedSlide>
		<img
			src="/flower.jpg"
			alt="Flower"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
	</FramedSlide>
	<FramedSlide part="inspiration" title="History">
		<div class="flex h-full flex-col justify-around gap-4">
			<div
				class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit gap-2 rounded-4xl p-6 shadow-inner"
			>
				<dl>
					<dt>Invention of Grading</dt>
					<dd>1785: Yale University</dd>
				</dl>
				<dl>
					<dt>Scarcity of positions (Oxford / Cambridge)</dt>
					<dd>1800 - 1900: from patronage to merit</dd>
					<dd>From apprenticeship to power-over dynamics</dd>
				</dl>
			</div>

			<iframe
				class="shadow-base-shadow w-full self-center rounded-4xl shadow-lg"
				title=""
				data-testid="embed-iframe"
				style="border-radius:12px"
				src="https://open.spotify.com/embed/episode/54y6QqXOFMOcFn0vOkj32B?utm_source=generator&si=469510dd65bb4afd"
				width="100%"
				height="352"
				frameBorder="0"
				allowfullscreen={false}
				allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
				loading="lazy"
			></iframe>
			<div
				class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit w-1/2 flex-col gap-2 rounded-4xl p-6 shadow-inner"
			>
				<dl>
					<dt>
						Today at <a href="https://goodlifecenter.yale.edu" class="link link-animated"
							>Yale Good Life Center</a
						>
					</dt>
					<dd>Trying to remove grading</dd>
				</dl>
			</div>
		</div>
		{#snippet footerRight()}
			<div class="text-xl">
				🙏 Thanks to <a
					href="https://www.cbs.dk/research/departments/department-management-society-and-communication/annemette-kjaergaard"
					class="link link-animated"
				>
					🌐 Annemette Kjærgaard
				</a>
			</div>
		{/snippet}
	</FramedSlide>
	<FramedSlide part="inspiration" section="books" title="Literature">
		<Library socketio={socketioBooks} />
		{#snippet footerLeft()}
			{#if booksQuestion && presenterMode}<QrCode
					url={getInputsUrl(page.url, 'cbs-books')}
					bind:modalHidden={qrCodeModalsHidden.books}
				/>{/if}
		{/snippet}
	</FramedSlide>
	<FramedSlide part="inspiration" section="law" title="Law">
		<div
			class="bg-secondary text-secondary-content shadow-base-shadow shadow-base-shadow m-5 grid grid-cols-[500px_1fr] gap-6 rounded-4xl p-6 shadow"
		>
			<div class="label col-span-2 text-8xl">Eksamensbekendtgørelesen</div>
			<div class="label text-[200px]">
				<Icon icon="fa6-solid:section" class="mr-0 inline size-[200px]" />11
			</div>
			<div class="text-left text-[70px]">
				All elements of the education <br /> finish with an exam.
			</div>
		</div>
	</FramedSlide>
	<FramedSlide part="inspiration" section="motivation" title="Motivation">
		<div class="mx-5 grid grid-cols-3 gap-10">
			<CardOverlay class="bg-primary text-primary-content z-50 pt-6 text-4xl" hidden={false}>
				<div class="mb-10 text-7xl font-bold">Relatedness</div>
				<div class="mb-6 pl-4 text-left text-5xl">Sense of belonging</div>
				<div class="mb-6 pl-4 text-left text-5xl">Community</div>
				<div class="mb-6 pl-4 text-left text-5xl">Connection</div>
				<div class="mb-6 pl-4 text-left text-5xl">Feeling cared for</div>
				<div class="mb-6 pl-4 text-left text-5xl">Ability to care for others</div>
			</CardOverlay>
			<CardOverlay
				class="bg-primary fragment fade-in text-primary-content z-50 pt-6 text-4xl"
				hidden={false}
			>
				<div class="mb-10 text-7xl font-bold">Autonomy</div>
				<div class="mb-6 pl-4 text-left text-5xl">Making your own decisions</div>
				<div class="mb-6 pl-4 text-left text-5xl">Be in the driver seat of your life</div>
				<div class="mb-6 pl-4 text-left text-5xl">Reflection</div>
			</CardOverlay>
			<CardOverlay
				class="bg-primary fragment fade-in text-primary-content z-50 pt-6 text-4xl"
				hidden={false}
			>
				<div class="mb-10 text-7xl font-bold">Competence</div>
				<div class="mb-6 pl-4 text-left text-5xl">Gaining mastery</div>
				<div class="mb-6 pl-4 text-left text-5xl">Being in flow</div>
				<div class="mb-6 pl-4 text-left text-5xl">Making an impact</div>
				<div class="mb-6 pl-4 text-left text-5xl">Build self-esteem</div>
			</CardOverlay>
		</div>
		{#snippet footerRight()}
			<div class="text-right text-xl">📖 Ib Ravn: Selvbestemmelsesteorien</div>
		{/snippet}
	</FramedSlide>
	<FramedSlide part="inspiration" section="motivation-examples" title="Motivation: Examples">
		<MotivationTable color="secondary" />
	</FramedSlide>
	<FramedSlide>
		<img
			src="/snow-lake.jpg"
			alt="Snow Lake"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
	</FramedSlide>
	<FramedSlide part="implementation" title="Inner change">
		<div class="flex flex-wrap justify-center gap-8">
			<ChatBubble variant="secondary" tailAngle={100} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">Trust based on<br />DTU's Honours Codex</div>
			</ChatBubble>
			<ChatBubble variant="secondary" tailAngle={130} tailLength={25} tailBase={10}>
				<div class="text-4xl font-bold">Everything is an invitation.</div>
			</ChatBubble>
			<ChatBubble variant="secondary" tailAngle={50} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">Starting Lectures with <br />guided meditation</div>
			</ChatBubble>
			<div class="w-[300px]"></div>
			<ChatBubble variant="secondary" tailAngle={130} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">No ambitions on <br />other peoples behalf!</div>
			</ChatBubble>
			<ChatBubble variant="secondary" tailAngle={160} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">No "deadlines" ☠️<br />only "living lines" 🌱.</div>
			</ChatBubble>
			<div class="w-[300px]"></div>
			<ChatBubble variant="secondary" tailAngle={130} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">You never disturb,<br />you always contribute.</div>
			</ChatBubble>
			<ChatBubble variant="secondary" tailAngle={305} tailLength={20} tailBase={10}>
				<div class="text-4xl font-bold">
					There's no way you can cheat<br />use, what's available to you.
				</div>
			</ChatBubble>
		</div>
	</FramedSlide>
	<FramedSlide part="implementation" section="practical" title="Outer change">
		<div class="mt-10 grid h-full grid-cols-2 gap-10 overflow-scroll">
			<div class="flex flex-col items-center gap-15">
				<button
					class="btn btn-xl btn-gradient btn-primary-container h-30 w-150 justify-center rounded-full p-10 text-5xl font-semibold shadow-inner"
					onclick={() => hideAllToggleOne('reflections', outerChange)}
				>
					Learning Reflections
				</button>
				<button
					class="btn btn-xl btn-gradient btn-primary-container h-30 w-150 justify-center rounded-full p-10 text-5xl font-semibold shadow-inner"
					onclick={() => hideAllToggleOne('closedQuestions', outerChange)}
				>
					Quantitative Questions
				</button>
				<button
					class="btn btn-xl btn-gradient btn-primary-container h-30 w-150 justify-center rounded-full p-10 text-5xl font-semibold shadow-inner"
					onclick={() => hideAllToggleOne('openQuestions', outerChange)}
				>
					Qualitative Questions
				</button>
			</div>
			<div class="flex flex-col items-center gap-10" bind:this={modulesContentColumn}>
				<CardOverlay
					class="bg-primary text-primary-content z-50 pt-6 text-4xl"
					bind:hidden={outerChange.reflections}
				>
					{#snippet header()}
						<div class="text-5xl font-bold">Learning Reflections</div>
					{/snippet}
					<dl>
						<dt>Course segementation</dt>
						<dd>4 modules in each course</dd>
						<dd>~ 2 - 4 weeks per module</dd>
						<dd>one learning reflection per module</dd>
					</dl>
					<dl class="pt-5">
						<dt>Question</dt>
						<dd class="italic">What have you learned in the last module?</dd>
						<dd>as the only mandatory sharing from the students</dd>
						<dd>only technical question</dd>
					</dl>

					<!-- <dl class="pt-5">
						<dt>Implementation</dt>
						<dd>via Microsoft Forms</dd>
						<dd>logged in user transferred automatically</dd>
						<dd>multiple hand-ins possible</dd>
					</dl> -->
				</CardOverlay>
				<CardOverlay
					class="bg-primary text-primary-content z-50 pt-6 text-4xl"
					bind:hidden={outerChange.closedQuestions}
				>
					{#snippet header()}
						<div class="text-5xl font-bold">Quantitative Questions</div>
					{/snippet}
					<dl>
						<dt>~ 30 quantitative questions per course</dt>
						<dd>x out of 5 rating</dd>
						<dd>some multiple choice</dd>
						<dd>some yes / no / maybe</dd>
					</dl>

					<dl class="pt-5">
						<dt>Content</dt>
						<dd>
							wellbeing<br />
							<ul>
								<li>responsibility</li>
								<li>fullfilment of needs</li>
								<li>motivation</li>
								<li>getting enough feedback</li>
								<li>distraction</li>
								<li>dicipline</li>
							</ul>
						</dd>
						<dd>use of teaching material and artificial intelligence</dd>
					</dl>
				</CardOverlay>
				<CardOverlay
					class="bg-primary text-primary-content z-50 pt-6 text-4xl"
					bind:hidden={outerChange.openQuestions}
				>
					{#snippet header()}
						<div class="text-5xl font-bold">Qualitative Questions</div>
					{/snippet}
					<dl>
						<dt>~10 open questions per course</dt>
						<dd>free text</dd>
						<dd>always one text field for <span class="italic">any comments</span></dd>
					</dl>
					<dl class="pt-5">
						<dt>Content</dt>
						<dd>use of teaching material and artificial intelligence</dd>
						<dd>
							motivation:<br />
							<ul>
								<li>sense of belonging</li>
								<li>autonomy</li>
								<li>competence</li>
							</ul>
						</dd>
						<dd>
							exam:<br />
							<ul>
								<li class="italic">
									What was good / bad about learning reflections instead of exams?
								</li>
							</ul>
						</dd>
					</dl>
				</CardOverlay>
			</div>
		</div>
	</FramedSlide>
	<FramedSlide>
		<img
			src="/besseggen.jpg"
			alt="Besseggen"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
	</FramedSlide>
	<FramedSlide part="results" title="Results: technical">
		<div class="flex w-full items-center gap-4 px-10 pb-32">
			{#snippet circularIcon(label: string)}
				<div
					bind:this={circularItems[label]}
					class="fragment relative h-15 w-15 shrink-0"
					{@attach toggleOnFragment(
						revealInstance!,
						() => connectorLines[label],
						'opacity-0',
						true
					)}
				>
					<div
						class="border-primary shadow-base-shadow flex h-15 w-15 flex-shrink-0 shrink items-center justify-center rounded-full border-4 bg-transparent shadow-lg"
					>
						<Icon
							class="text-primary-container size-8"
							icon="fluent-emoji-high-contrast:thinking-face"
						/>
					</div>
					<div class="absolute top-full left-1/2 mt-2 w-56 -translate-x-1/2 text-center">
						{label}
					</div>
				</div>
			{/snippet}
			{@render circularIcon('Start')}
			<div
				bind:this={connectorLines['Learning Reflection 1']}
				class="bg-primary shadow-base-shadow h-2 grow rounded opacity-0 shadow-lg transition-opacity"
			></div>
			{@render circularIcon('Learning Reflection 1')}
			<div
				bind:this={connectorLines['Learning Reflection 2']}
				class="bg-primary shadow-base-shadow h-2 grow rounded opacity-0 shadow-lg transition-opacity"
			></div>
			{@render circularIcon('Learning Reflection 2')}
			<div
				bind:this={connectorLines['Learning Reflection 3']}
				class="bg-primary shadow-base-shadow h-2 grow rounded opacity-0 shadow-lg transition-opacity"
			></div>
			{@render circularIcon('Learning Reflection 3')}
			<div
				bind:this={connectorLines['Learning Reflection 4']}
				class="bg-primary shadow-base-shadow h-2 grow rounded opacity-0 shadow-lg transition-opacity"
			></div>
			{@render circularIcon('Learning Reflection 4')}
			<div
				bind:this={connectorLines.Closing}
				class="bg-primary shadow-base-shadow h-2 grow rounded opacity-0 shadow-lg transition-opacity"
			></div>
			{@render circularIcon('Closing')}
		</div>
		<div class="grid h-3/4">
			<!-- <div class="fragment fade-in-then-out col-start-1 row-start-1 mt-30">
				<ChatBubble variant="secondary" tailAngle={160} tailLength={35} tailBase={15}>
					<div class="text-4xl font-bold">No "deadlines" ☠️<br />only "living lines" 🌱.</div>
				</ChatBubble>
			</div> -->
			<div
				class="fragment fade-in-then-out bg-primary-container text-primary-container-content shadow-base-shadow absolute top-1/2 left-1/2 col-start-1 row-start-1 mt-30 flex h-50 w-150 -translate-x-1/2 -translate-y-1/2 transform items-center justify-center rounded-[50%] text-5xl font-bold shadow"
			>
				No "deadlines" ☠️<br />
				only "living lines" 🌱!
			</div>
			<div class="fragment col-start-1 row-start-1">
				<CardOverlay
					class="bg-primary fragment text-primary-content z-50 pt-6 text-4xl"
					hidden={false}
					// bind:hidden={hideModules.openQuestions}
				>
					{#snippet header()}
						<div class="text-5xl font-bold">Story: Closing of Master Course - Fall 2025</div>
					{/snippet}
					<dl>
						<dt>3 out of 4 learning reflections <span class="italic">mandatory</span></dt>
					</dl>
					<dl>
						<dt>Last lecture</dt>
						<dd>Only 8 out of 74 students missing to hand at least 3.</dd>
					</dl>
					<dl>
						<dt>Reminder</dt>
						<dd>Personal to the 8 missing: asking how much more time they need.</dd>
						<dd>Announcement to all, that those emails were sent.</dd>
						<dd>3 days after all missing mandatory reflections shared.</dd>
					</dl>

					<dl class="pt-5">
						<dt>One week after reminder</dt>
						<dd>70 % handed in all 4 learning reflections.</dd>
					</dl>
				</CardOverlay>
			</div>
			<!-- <CardOverlay
				class="bg-primary-container text-primary-container-content z-50 pt-6 text-4xl"
				hidden={false}
				// bind:hidden={hideModules.openQuestions}
			>
				{#snippet header()}
					<div class="text-5xl font-bold">Learning Reflection 1</div>
				{/snippet}
				<dl>
					<dt>What have you learned about module 1?</dt>
				</dl>
				<dl class="pt-5">
					<dt>Questions on Meditation</dt>
					<dd>More mediations: yes / no / maybe</dd>
					<dd>How was it to start the lecture with a meditation?</dd>
				</dl>
			</CardOverlay> -->
		</div>
		<!-- <div class="flex w-full items-center gap-4 px-10">
			{#snippet courseParts(labels: string[])}
				{#each labels as label, index (index)}
					<div class="flex items-center gap-4 {index < labels.length - 1 ? 'grow' : ''}">
						<div class="grid grid-cols-1 items-center gap-2">
							<div
								class="border-secondary shadow-base-shadow flex h-15 w-15 flex-shrink-0 items-center justify-center rounded-full border-4 bg-transparent shadow-lg"
							>
								<Icon
									class="text-secondary-container fragement size-8"
									icon="fluent-emoji-high-contrast:thinking-face"
								/>
							</div>
							{label}
						</div>
						{#if index < labels.length - 1}
							<div class="bg-secondary shadow-secondary h-2 grow rounded shadow-lg"></div>
						{/if}
					</div>
				{/each}
			{/snippet}
			{@render courseParts([
				'Start',
				'Learning Reflection 1',
				'Learning Reflection 2',
				'Learning Reflection 3',
				'Learning Reflection 4',
				'Reminder'
			])}
		</div> -->
	</FramedSlide>
	<FramedSlide part="results" section="meditation" title="Results: meditation">
		<div>Would you like to have more meditations?<br />&nbsp;</div>
		<DivergingStackedChart
			data={meditationData}
			categories={['no', 'maybe', 'yes']}
			color="primary"
		/>
	</FramedSlide>
	<FramedSlide part="results" section="learning-more" title="Results: learning more">
		<div>Reflecting on my own learning,<br /> I learn more, than in a course with exam...</div>
		<DivergingStackedChart data={learnedMoreData} categories={categoriesNoExam} color="primary" />
	</FramedSlide>
	<FramedSlide part="results" section="motivation" title="Results: motivation">
		<div>
			Reflecting on my own learning, <br />I can stay more <span class="italic">motivated</span>,
			than in a course with exam
		</div>
		<DivergingStackedChart data={moreMotivatedData} categories={categoriesNoExam} color="primary" />
	</FramedSlide>
	<FramedSlide part="results" section="responsibility" title="Results: responsibility">
		<div>
			Reflecting on my own learning, <br />I take more <span class="italic">responsibility</span> for
			my own learning, than in a course with exam
		</div>
		<DivergingStackedChart
			data={moreResponsibilityData}
			categories={categoriesNoExam}
			color="primary"
		/>
	</FramedSlide>
	<!-- <FramedSlide part="results" section="quantitative">
		Quantitative results: learning, responsibility, meditation, sharing comments
	</FramedSlide> -->
	<!-- <div>Summary from 2000+ answers</div> -->
	<FramedSlide part="results" section="qualitative-good" title="Results: qualitative">
		<div class="my-5 grid h-full grid-cols-2 grid-rows-[auto_minmax(0,1fr)] gap-4">
			<div class="col-span-2 min-h-0">
				👍 What was good about having the learning reflections <br />instead of other exam forms in
				this course? (524 answers)
			</div>
			<div class="h-full overflow-y-scroll">
				<div
					class="fragment fade-in bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-4 text-4xl shadow-inner"
				>
					<DataList
						title="~2/3: less stress, more well-being"
						content={[
							'less <span class="italic">stress, anxiety, pressure</span>.',
							'<span class="italic">Healthier mindset</span>; fewer anxiety triggers.',
							'Frees <span class="italic">mental bandwidth</span> to reflect rather than rush.',
							'Supports <span class="italic">well-being</span>; learning feels more <span class="italic">sustainable</span>.'
						]}
						color="secondary"
					/>
				</div>
				<div
					class="fragment fade-in bg-secondary text-secondary-content shadow-base-shadow mt-4 flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-4 text-4xl shadow-inner"
				>
					<DataList
						title="~1/2: deeper learning"
						content={[
							'Focus on <span class="italic">understanding</span> and learning rather than cramming an exam.',
							'Calmer pacing improves <span class="italic">confidence</span> with difficult topics.'
						]}
						color="secondary"
					/>
				</div>
				<div
					class="fragment fade-in bg-secondary text-secondary-content shadow-base-shadow mt-4 flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-4 text-4xl shadow-inner"
				>
					<DataList
						title="Freedom to explore"
						content={[
							'Encourages <span class="italic">curiosity</span> instead of formula-driven exam preparation.',
							'Allows <span class="italic">deeper dives</span> into topics of interest.',
							'Removes <span class="italic">fear</span> of "falling behind".'
						]}
						color="secondary"
					/>
				</div>
			</div>
			<div class="h-full overflow-y-scroll">
				<div
					class="fragment fade-in bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-4 text-4xl shadow-inner"
				>
					<DataList
						title="Flexibility"
						content={[
							'Own-tempo: easier to <span class="italic">adjust workload</span>.',
							'<span class="italic">Shift effort</span> between courses possible.',
							'Frees <span class="italic">mental bandwidth</span> to reflect.',
							'<span class="italic">Autonomy</span> increases enjoyment of content.',
							'More time to <span class="italic">revisit challenging topics</span>.'
						]}
						color="secondary"
					/>
				</div>
				<div
					class="fragment fade-in bg-secondary text-secondary-content shadow-base-shadow mt-5 flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-4 text-4xl shadow-inner"
				>
					<DataList
						title="Reflections support understanding"
						content={[
							'Forces <span class="italic">consolidation</span> after each topic.',
							'<span class="italic">Strengthens memory</span> of new insight.',
							'Creates <span class="italic">awareness</span> of what is understood.',
							'Promotes <span class="italic">personal ownership</span>.'
						]}
						color="secondary"
					/>
				</div>
				<div
					class="fragment fade-in bg-secondary text-secondary-content shadow-base-shadow mt-4 flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-4 text-4xl shadow-inner"
				>
					<DataList
						title="Course setup"
						content={[
							'Structured <span class="italic">e-learning environment</span> appreciated.',
							'Quizzes provide <span class="italic">small checks without pressure</span>.',
							'Course <span class="italic">atmosphere</span> perceived as <span class="italic">motivating and friendly</span>.'
						]}
						color="secondary"
					/>
				</div>
			</div>
		</div>
	</FramedSlide>
	<FramedSlide part="results" section="qualitative-bad" title="Results: qualitative">
		<div class="my-5 grid h-full grid-cols-2 grid-rows-[auto_minmax(0,1fr)] gap-4">
			<div class="col-span-2 min-h-0">
				👎 What was bad about having the learning reflections <br />instead of other exam forms in
				this course? (508 answers)
			</div>
			<div class="h-full overflow-scroll">
				<div
					class="fragment fade-in bg-primary text-primary-content shadow-base-shadow flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-4 text-4xl shadow-inner"
				>
					<DataList
						title="Motivation drop"
						content={[
							'Hard to stay <span class="italic">disciplined</span> when other courses pile up pressure.',
							'<span class="italic">Momentum weakens</span> during busy periods in <span class="italic">other courses</span>.',
							'Self-driven learning <span class="italic">feels difficult</span> for part of the group.'
						]}
					/>
				</div>
				<div
					class="fragment fade-in bg-primary text-primary-content shadow-base-shadow mt-4 flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-4 text-4xl shadow-inner"
				>
					<DataList
						title="Exercise solutions"
						content={[
							'Need for <span class="italic">solutions</span> to verify understanding.',
							'Desire for <span class="italic">mandatory checkpoints</span> to maintain engagement.'
						]}
					/>
				</div>
			</div>
			<div class="h-full overflow-scroll">
				<div
					class="fragment fade-in bg-primary text-primary-content shadow-base-shadow flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-4 text-4xl shadow-inner"
				>
					<DataList
						title="Individual perception"
						content={[
							'High <span class="italic">self-discipline</span> differs from person to person.',
							'Low external pressure reveals who needs <span class="italic">more structure</span>.',
							'Different preferences between <span class="italic">media: videos, quizzes, book, lectures</span>.'
						]}
					/>
				</div>
				<div
					class="fragment fade-in bg-primary text-primary-content shadow-base-shadow mt-5 flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-4 text-4xl shadow-inner"
				>
					<DataList
						title="Experimental"
						content={[
							'Feeling of being a "<span class="italic">guinea pig</span>".',
							'Need for <span class="italic">small guard rails</span>.',
							'Format works well if <span class="italic">more courses</span> align with same philosophy.'
						]}
					/>
				</div>
			</div>
		</div>
	</FramedSlide>
	<!-- {#each data.payload.qualitativeFeedbackSnapshot.entities as feedback, idx (idx)}
		<FramedSlide part="results" section={`qualitative-${idx}`} title="Results: qualitative">
			<QualitativeFeedback content={feedback.content} />
		</FramedSlide>
	{/each} -->
	<FramedSlide part="results" section="emotional" title="Results: emotional">
		<div class="flex min-h-screen items-center justify-center">
			<Icon icon="fluent-emoji-flat:heart-hands" class="h-[600px] w-[600px]" />
		</div>
	</FramedSlide>
	<FramedSlide part="results" section="colleagues" title="Results: colleagues">
		<div class="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] place-items-center gap-8">
			<div
				class="fragment fade-out bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-5 shadow-inner"
				data-fragment-index="0"
			>
				<dl>
					<dt>Interviewed colleagues</dt>
					<dd>from 6 follow-up courses</dd>
					<dd>where my courses are prerequisites</dd>
				</dl>
			</div>
			<Icon
				icon="at-icons:arrow-right"
				class="fragment fade-out size-30 self-center"
				data-fragment-index="0"
			/>
			<div
				class="fragment fade-out bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 rounded-4xl p-5 shadow-inner"
				data-fragment-index="0"
			>
				<dl>
					<dt>No indication that students know less</dt>
					<dd>all pleased with students preparation</dd>
				</dl>
			</div>
			<div
				class="fragment fade-in-then-out bg-primary text-primary-content shadow-base-shadow 3 absolute col-span-3 flex h-fit flex-col gap-2 rounded-4xl p-5 shadow-inner"
				data-fragment-index="0"
			>
				<dl>
					<dt>One colleage went anonymously to press</dt>
					<dd>screenshots of my teaching material</dd>
					<dd>judges: "bad videos" and "incomprehensible exercises"</dd>
					<dd>
						🗞️ Ingeniøren: <a
							href="https://ing.dk/artikel/dtu-drops-exams-students-can-decide-themselves-if-they-have-passed"
							target="_blank"
							rel="noopener noreferrer">DTU drops exams</a
						>
					</dd>
				</dl>
			</div>
			<div class="fragment fade-in absolute col-span-3 w-full" data-fragment-index="2">
				<ChatBubble variant="secondary" class="p-8" tailAngle={130} tailLength={100} tailBase={40}>
					<div class="mt-5 mb-3 text-5xl italic">
						🥥 "You are getting hit, because you shake the coconut tree. And in a way I wish you to
						get hit, because it means you are not loosing ground, you continue to crack the nut."<br
						/>
					</div>
					Christèle Galpin, cofounding manager,
					<a href="https://www.alfalfaz.com/en/home/" target="_blank" rel="noopener noreferrer"
						>Alfalfaz</a
					>*
				</ChatBubble>
			</div>
		</div>
		{#snippet footerRight()}
			<div class="fragment text-right text-xl" data-fragment-index="2">
				* Christèle and I are "travel companions" on the <a
					href="https://www.regenerators.co"
					target="_blank"
					rel="noopener noreferrer"
					>Regenerative Leadership Journey 2026
				</a>
				by Laura Storm
			</div>
		{/snippet}
	</FramedSlide>
	<FramedSlide part="results" section="inner-development" title="Results: reflection">
		<div class=" flex flex-wrap justify-center gap-5 px-10">
			<div
				class="bg-primary-container text-primary-container-content shadow-base-shadow m-5 flex h-fit w-fit items-center justify-center rounded-[50%] p-10 text-5xl font-bold shadow"
			>
				Integrity
			</div>
			<div
				class="bg-primary-container text-primary-container-content shadow-base-shadow m-5 flex h-fit w-fit items-center justify-center rounded-[50%] p-10 text-5xl font-bold shadow"
			>
				Meaning
			</div>
			<div
				class="bg-primary-container text-primary-container-content shadow-base-shadow m-5 flex h-fit w-fit items-center justify-center rounded-[50%] p-10 text-5xl font-bold shadow"
			>
				Resilience
			</div>
			<div
				class="bg-primary-container text-primary-container-content shadow-base-shadow m-5 flex h-fit w-fit items-center justify-center rounded-[50%] p-10 text-5xl font-bold shadow"
			>
				Inner <br /> Growth
			</div>
			<div
				class="bg-primary-container text-primary-container-content shadow-base-shadow m-5 flex h-fit w-fit items-center justify-center rounded-[50%] p-10 text-5xl font-bold shadow"
			>
				Connection <br /> to Nature
			</div>
			<div
				class="bg-primary-container text-primary-container-content shadow-base-shadow m-5 flex h-fit w-fit items-center justify-center rounded-[50%] p-10 text-5xl font-bold shadow"
			>
				Strength
			</div>
			<div
				class="bg-primary-container text-primary-container-content shadow-base-shadow m-5 flex h-fit w-fit items-center justify-center rounded-[50%] p-10 text-5xl font-bold shadow"
			>
				Time
			</div>
			<div
				class="bg-primary-container text-primary-container-content shadow-base-shadow m-5 flex h-fit w-fit items-center justify-center rounded-[50%] p-10 text-5xl font-bold shadow"
			>
				No more <br />reports
			</div>
		</div>
		<div class="fragment fade-in w-full" data-fragment-index="2">
			<ChatBubble variant="secondary" tailAngle={210} tailLength={80} tailBase={40}>
				<div class="mt-5 mb-3 text-5xl italic">
					<Icon icon="mdi:autorenew" class="mr-2 inline-block size-4" /> "You are the person, that I have
					seen <br />
					changing most over the last 10 years."
				</div>
				<a
					href="https://www.dtu.dk/english/person/tiberiu-gabriel-zsurzsan?id=62516&entity=profile"
					target="_blank"
					rel="noopener noreferrer">Tiberiu Gabriel Zsurzsan</a
				>, close colleague
			</ChatBubble>
		</div>
	</FramedSlide>
	<FramedSlide>
		<img
			src="/clouds-jotunheimen.jpg"
			alt="Clouds Jotunheimen"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
	</FramedSlide>
	<FramedSlide part="inner-change" title="Inner change?" hideProgressBar>
		<div class="label text-9xl font-bold">
			Who wants <br /> <span class="fragment">to</span> change?
		</div>
		<div
			class="fragment base-content-variant bg-base-300 shadow-base-shadow absolute top-1/10 left-0 m-5 rounded-[50%] p-15 shadow"
		>
			How can you connect deeper to your inner nature?
		</div>
		<div
			class="fragment base-content-variant bg-base-300 shadow-base-shadow absolute top-1/10 left-7/10 m-5 rounded-[50%] p-15 shadow"
		>
			What can you start doing today,<br />
			to love yourself more?
		</div>
		<div
			class="fragment base-content-variant bg-base-300 shadow-base-shadow absolute top-7/10 left-0 m-5 rounded-[50%] p-15 shadow"
		>
			How are you affected by the <br />
			coloniality of the last 1-7 generations?
		</div>
		<div class="fragment absolute top-6/10 left-8/10">
			<Icon icon="andrsrxn:playing-heart" class="text-error text-[250px]" />
		</div>
		<!-- Session around bonfire! -->
		{#snippet footerRight()}
			<div class="text-right text-xl">
				🤔 Inspired by <a
					href="https://www.linkedin.com/in/jacob-rask-b4b805139/"
					class="link link-animated">Jacob Rask</a
				>
			</div>
		{/snippet}
	</FramedSlide>
	<FramedSlide>
		<img
			src="/sunset-vejlesoen.jpg"
			alt="Sunset Vejlesøen"
			class="shadow-base-shadow h-fit w-3/4 self-center rounded-4xl shadow-lg"
		/>
	</FramedSlide>
	<FramedSlide part="comments-and-questions" hideProgressBar>
		{#if commentsQuestion}
			<Comments socketio={socketioComments} {presenterMode} />
		{:else}
			{@render interactiveElementNotAvailable('comments and questions dialog')}
		{/if}
		{#snippet footerLeft()}
			{#if commentsQuestion && presenterMode}<QrCode
					url={getInputsUrl(page.url, 'cbs-comments')}
					bind:modalHidden={qrCodeModalsHidden.comments}
				/>{/if}
		{/snippet}
	</FramedSlide>
	<!-- <FramedSlide>
		planetary boundaries -> inner work -> trust<br />
		stressed people -> stressed systems -> stressed planet (from regenerative leadership)
	</FramedSlide> -->
	<FramedSlide part="others-engagement" title="What are others doing?">
		<div class="grid h-full grid-cols-2 gap-6">
			<div
				class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-6 text-4xl shadow-inner"
			>
				<div class="text-center text-5xl font-bold">Arnolds encounters</div>
				<ul class="list-disc space-y-2">
					<li>
						<a
							href="https://www.cbs.dk/research/departments/department-management-society-and-communication/annemette-kjaergaard"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Annemette Kjærgaard</a
						>, Copenhagen Business School
					</li>
					<li>
						<a
							href="https://www.cefu.dk/emner/om-cefu/forskere/noemi-katznelson.aspx"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Noemi Katznelson</a
						>, Aalborg University
					</li>
					<li>
						<a
							href="https://rflect.ch/"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">rflect.ch</a
						>, Switzerland
					</li>
					<li>
						<a
							href="https://www.regenerative-educators.com/theartofregenerativeeducatorship"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Regenerative Educatorship</a
						>, The Netherlands/Belgium
					</li>
					<li>
						<a
							href="https://www.jacobrask.dk"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Jacob Rask</a
						>, Roskilde University
					</li>
					<li>
						<a
							href="https://www.keg.lu.se/en/vasna-ramasar"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Vasna Ramasar</a
						>, Lund University
					</li>
					<li>
						<a
							href="https://ibi.ethz.ch/en/das-institut/people/person-detail.tobias-luthe.html"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Tobias Luthe</a
						>, ETH Zürich
					</li>
					<li>
						<a
							href="https://www.opheinonen.com/bio"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Olli-Pekka Heinonen</a
						>, International Baccalaureate
					</li>
				</ul>
			</div>
			<div
				class="bg-secondary text-secondary-content shadow-base-shadow flex h-fit flex-col gap-2 overflow-y-auto rounded-4xl p-6 text-4xl shadow-inner"
			>
				<div class="text-center text-5xl font-bold">Selected sources from Annemette</div>
				<ul class="list-disc space-y-2">
					<li>
						<a
							href="https://www.alfiekohn.org"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Alfie Kohn</a
						>, Author and Educator
					</li>
					<li>
						<a
							href="https://www.emich.edu/cob/faculty/j_beatty.php"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Joy Beatty</a
						>, Eastern Michigan University
					</li>
					<li>
						<a
							href="https://profiles.ucl.ac.uk/52741-stuart-tannock/publications"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Stuart Tannock</a
						>, University College London
					</li>
					<li>
						<a
							href="https://link.springer.com/article/10.1007/s10459-009-9211-1"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Casey B. White</a
						>, University of Michigan Medical School
					</li>
					<li>
						<a
							href="https://www.tandfonline.com/doi/full/10.1080/0309877X.2019.1619073"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Chris McMorran</a
						>, National University of Singapore
					</li>
					<li>
						<a
							href="https://academic.oup.com/academicmedicine/article-abstract/84/5/655/8353384?redirectedFrom=fulltext"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Robert A. Bloodgood</a
						>, University of Virginia School of Medicine
					</li>
					<li>
						<a
							href="https://www.mayoclinicproceedings.org/article/S0025-6196(11)61250-0/abstract"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Daniel E. Rohe</a
						>, Mayo Clinic
					</li>
					<li>
						<a
							href="https://www.tandfonline.com/doi/full/10.1080/13562510902757260"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Lars O. Dahlgren</a
						>, Linköping University
					</li>
					<li>
						<a
							href="https://www.tandfonline.com/doi/full/10.3109/0142159X.2012.652243"
							class="link link-animated"
							target="_blank"
							rel="noopener noreferrer">Faysal Altahawi</a
						>, Case Western Reserve University
					</li>
				</ul>
			</div>
		</div>
	</FramedSlide>
	{#if presenterMode}
		<FramedSlide part="bonfire" title="Invitation to Bonfire Session" hideProgressBar>
			<div class="grid h-full min-h-0 grid-cols-2 grid-rows-[minmax(0,1fr)] items-center gap-6">
				<video
					class="shadow-base-shadow max-h-full w-3/4 justify-self-center rounded-4xl object-fill shadow-lg"
					controls
					src="/teachingengagement/bonfire.mp4"><track default kind="captions" /></video
				>
				<div class="flex flex-col items-center justify-center gap-4">
					{#await qrCodeEmailPromise}
						<p>Generating QR code…</p>
					{:then qrCodeEmailUrl}
						<img src={qrCodeEmailUrl} class="h-150 w-150" alt="QR Code for email" />
					{/await}
					<a
						href="mailto:knott@dtu.dk?subject=Follow-up on CBS Library event, November 2nd 2026"
						class="link link-animated"
					>
						knott@dtu.dk
					</a>
				</div>
			</div>
		</FramedSlide>
	{/if}
	<FramedSlide part="terms-and-conditions">
		<TermsAndConditions presentationMode />
		{#if returnToSlide}
			<div>
				<span class="icon-[fa-regular--hand-point-right] mr-4 size-7"></span>Back to
				<a href="#{returnToSlide}" class="link link-animated"
					>{returnToSlide.replaceAll('-', ' ')}</a
				>.
			</div>
		{/if}
	</FramedSlide>
</RevealJs>

<style>
	dl {
		margin-left: 10px !important;
		margin-right: 10px !important;
		padding-left: 30px !important;
		padding-right: 30px !important;
	}
	dt {
		font-style: italic;
	}
</style>
