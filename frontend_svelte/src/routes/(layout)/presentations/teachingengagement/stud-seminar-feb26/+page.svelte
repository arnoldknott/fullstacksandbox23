<script lang="ts">
	import type { PageData } from './$types';
	import RevealJS from '$components/RevealJS.svelte';
	import FramedSlide from './FramedSlide.svelte';
	import ChatBubble from '$components/ChatBubble.svelte';
	import DivergingStackedChart from './DivergingStackedChart.svelte';
	import SlideTitle from './SlideTitle.svelte';
	import QualitativeFeeback from './QualitativeFeeback.svelte';
	import Display from '$components/Display.svelte';
	import MotivationTable from './MotivationTable.svelte';
	// import { marked } from 'marked';

	let { data }: { data: PageData } = $props();
	// console.log('=== 🧦 presentation - devF23 - motivation - page.questionsData.feedback ===');
	// console.log(data.questionsData.feedback);

	type LearnSetupEntry = {
		year: number;
		comparison: number[];
	};

	type NoExamEntry = {
		year: number;
		course?: string;
		learnedMore: number[];
		takeMoreResponsibility: number[];
		moreMotivated: number[];
	};

	// type AgreementEntry = {
	// 	year: number;
	// 	'totally disagree': number;
	// 	disagree: number;
	// 	same: number;
	// 	agree: number;
	// 	'fully agree': number;
	// };

	// const categoriesTools: [string, string, string, string, string] = ['totally disagree', 'disagree', 'same', 'agree', 'fully agree'];

	// const toolsData = [
	// 	{// using Brightspace as is
	// 	    year: 2021,
	// 	    course: "31003",
	// 		learnedALot:  [0, 2, 6, 13, 30],
	// 		toolsDTULearn: [11, 9, 8, 12, 2],
	// 		toolsDiscord: [0, 1, 7, 9, 24],
	// 		toolsMSForms: [3, 1, 10, 22, 6],
	// 		toolsYouTube: [0, 1, 3, 14, 24],
	// 		toolsLab: [0, 5, 9, 11, 16]
	// 	},
	// 	{// using Brightspace as is
	// 	    year: 2021,
	// 	    course: "31351",
	// 		learnedALot:  [0, 0, 0, 7, 13],
	// 		toolsDTULearn: [3, 1, 6, 4, 2],
	// 		toolsDiscord: [0, 1, 1, 4, 10],
	// 		toolsMSForms: [1, 1, 9, 3, 1],
	// 		toolsYouTube: [0, 0, 1, 7, 8],
	// 		toolsLab: [0, 0, 1, 2, 13]
	// 	},
	// 	{// in 2022: protoptype in Vanilla Javascript
	// 	    year: 2022,
	// 	    course: "31003",
	// 		learnedALot:  [1, 1, 5, 13, 21],
	// 		learnSetup: [0, 2, 6, 10, 17],
	// 		toolsDTULearn: [0, 2, 5, 17, 17],
	// 		toolsDiscord: [0, 3, 6, 9, 17],
	// 		toolsMSForms: [3, 5, 5, 15, 5],
	// 		toolsYouTube: [1, 3, 5, 7, 12, 11],
	// 		toolsLab: [1, 2, 7, 10, 13]
	// 	},
	// 	{// in 2022: protoptype in Vanilla Javascript
	// 	    year: 2022,
	// 	    course: "31039",
	// 		learnedALot:  [0, 1, 4, 6, 8],
	// 		learnSetup: [0, 0, 4, 3, 9],
	// 		toolsDTULearn: [0, 0, 0, 6, 9],
	// 		toolsDiscord: [0, 1, 1, 5, 9],
	// 		toolsMSForms: [0, 3, 4, 3, 4],
	// 		toolsYouTube: [0,0,0,5, 11],
	// 		toolsLab: [0, 0, 2, 5, 9]
	// 	},
	// 	{// in 2022: protoptype in Vanilla Javascript
	// 	    year: 2022,
	// 	    course: "31351",
	// 		learnedALot:  [0, 0, 1, 7, 9],
	// 		learnSetup: [0, 1, 2, 7, 5],
	// 		toolsDTULearn: [0, 1, 1, 5, 8],
	// 		toolsDiscord: [1, 2, 2, 7, 3],
	// 		toolsMSForms: [1, 1, 2, 5, 3],
	// 		toolsYouTube: [1, 0, 4, 5, 5],
	// 		toolsLab: [0, 0, 3, 4, 8]
	// 	},
	// 	{// in 2023: Vue+Nuxt implementation
	// 	    year: 2023,
	// 	    course: "34601",
	// 		learnedALot:  [0, 0, 2, 1, 18],
	// 		learnSetup: [1, 0, 7, 12, 11],
	// 		toolsDTULearn: [1, 0, 7, 12, 11],
	// 		toolsDiscord: [0, 1, 1, 13, 16],
	// 		toolsMSForms: [4, 3, 11, 9, 4],
	// 		toolsYouTube: [1, 2, 6, 14, 7],
	// 		toolsLab: [0, 0, 2, 16, 11]
	// 	},
	// 	{// in 2023: Vue+Nuxt implementation
	// 	    year: 2023,
	// 	    course: "34620",
	// 		learnedALot:  [0, 0, 4, 4, 7],
	// 		learnSetup: [1, 1, 1, 5, 6],
	// 		toolsDTULearn: [0, 1, 1, 6, 6],
	// 		toolsDiscord: [1, 0, 4, 5, 4],
	// 		toolsMSForms: [1, 1, 4, 7, 1],
	// 		toolsYouTube: [1, 2, 1, 8, 2],
	// 		toolsLab: [0, 0, 2, 7, 5]
	// 	},
	// ];

	const learnCategories: [string, string, string, string, string] = [
		'much worse',
		'worse',
		'same',
		'better',
		'much better'
	];

	const learnSetup: LearnSetupEntry[] = [
		{
			year: 2022,
			comparison: [0, 5, 18, 30, 47]
		},
		{
			year: 2023,
			comparison: [5, 2, 12, 42, 40]
		},
		{
			year: 2024,
			comparison: [5, 10, 15, 21, 38]
		},
		{
			year: 2025,
			comparison: [5, 9, 11, 38, 47]
		}
	];

	const categoriesNoExam: [string, string, string, string, string] = [
		'totally disagree',
		'disagree',
		'same',
		'agree',
		'fully agree'
	];

	// Data follows the categories order above
	const noExamData: NoExamEntry[] = [
		{
			year: 2024,
			course: '34654',
			learnedMore: [4, 9, 33, 11, 9],
			takeMoreResponsibility: [1, 7, 13, 28, 17],
			moreMotivated: [4, 15, 16, 18, 13]
		},
		{
			year: 2025,
			course: '34601',
			learnedMore: [5, 29, 45, 22, 8],
			takeMoreResponsibility: [3, 23, 37, 30, 15],
			moreMotivated: [7, 28, 37, 23, 14]
		},
		{
			year: 2025,
			course: '34620',
			learnedMore: [7, 37, 58, 26, 9],
			takeMoreResponsibility: [6, 24, 34, 52, 21],
			moreMotivated: [7, 31, 46, 38, 14]
		},
		{
			year: 2025,
			course: '34654',
			learnedMore: [1, 6, 28, 13, 9],
			takeMoreResponsibility: [1, 4, 17, 22, 13],
			moreMotivated: [2, 10, 18, 19, 8]
		}
	];

	const learnSetupData = learnSetup.map((entry) => ({
		year: entry.year,
		values: entry.comparison
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

	const sentimentColors = {
		'much better': 'bg-success-content',
		better: 'bg-success',
		same: 'bg-warning',
		worse: 'bg-error',
		'much worse': 'bg-error-content',
		'fully agree': 'bg-success-content',
		agree: 'bg-success',
		disagree: 'bg-error',
		'totally disagree': 'bg-error-content'
	};

	// 	const markdownComment = `# Heading

	// This is a **markdown** response with _formatting_.

	// - It supports lists
	// - And other markdown features

	// ## Second heading

	// ### Third Heading

	// [Here's a link](https://www.example.com)`;

	// const markdownCommentHtml = marked.parse(markdownComment, { async: false });

	// const learnSetupCategories: [string, string, string, string, string] = [
	// 	'much better',
	// 	'better',
	// 	'same',
	// 	'worse',
	// 	'much worse'
	// ];

	// const agreementCategories: [string, string, string, string, string] = [
	// 	'fully agree',
	// 	'agree',
	// 	'same',
	// 	'disagree',
	// 	'totally disagree'
	// ];
</script>

<RevealJS>
	<section>
		<div class="display-large text-secondary pb-20 text-9xl font-bold">
			Teaching Engagement
			<br />
			without Exams
		</div>
		<div class="display text-primary pb-10 font-semibold">Arnold Knott</div>
		<div class="display text-success/80 font-semibold">DTU Elektro</div>
	</section>
	<section class="display">
		<!-- <SlideTitle>Welcome</SlideTitle> -->
		<Display>Welcome</Display>
		<ul class="display-small mt-5 list-inside !list-none">
			<li class="fragment mt-3">
				<span class="icon-[game-icons--greek-temple] size-12"></span> My old school teaching
			</li>

			<ul class="list-inside !list-none">
				<li class="text-error fragment mt-3">
					<span class="icon-[streamline-plump--cog-automation] size-12"></span> Automation (2010 - 2019)
				</li>
				<li class="text-warning fragment mt-3">
					<span class="icon-[tabler--palette] size-12"></span> Design (2020 - 2023)
				</li>
			</ul>
			<li class="text-primary fragment mt-3">
				<span class="icon-[healthicons--i-exam-multiple-choice-outline] size-12"></span> No exam (2024
				- now)
			</li>
			<ul class="list-inside !list-none">
				<li class="text-neutral fragment mt-3 opacity-60">
					<span class="icon-[f7--book] size-12"></span> Theory on motivation
				</li>
				<li class="text-info fragment mt-3 opacity-60">
					<span class="icon-[ri--tools-fill] size-12"></span> Implementation
				</li>
				<li class="text-accent fragment mt-3 opacity-75">
					<span class="icon-[uim--graph-bar] size-12"></span> Results
				</li>
				<li class="text-primary fragment mt-3 opacity-90">
					<span class="icon-[lsicon--view-outline] size-12"></span> Outlook
				</li>
			</ul>
		</ul>
	</section>
	<section>
		<div class="r-strech">
			<Display><div class="text-error">Automation<br />(2010 - 2019)</div></Display>
		</div>
	</section>
	<FramedSlide section="old" content={['automation', '']}>
		<iframe
			title="Assessment Adventures"
			src="/teachingengagement/assessment-adventures-2021-10.pdf"
			class="shadow-error h-full w-full rounded-4xl object-contain shadow-lg"
		>
		</iframe>
	</FramedSlide>
	<FramedSlide section="old" content={['automation', '']}>
		<iframe
			title="Assessment Adventures"
			src="https://panopto.dtu.dk/Panopto/Pages/Embed.aspx?id=1f01afc8-dcc5-49d8-9580-af130048908e&autoplay=false&offerviewer=false&showtitle=true&showbrand=false&captions=false&interactivity=all"
			height="100%"
			width="100%"
			allowfullscreen
			allow="autoplay"
			class="shadow-error max-h-full rounded-4xl object-contain shadow-lg"
		>
		</iframe>
	</FramedSlide>
	<FramedSlide section="old" content={['automation', '']}>
		<SlideTitle color="secondary">Inspiration from back then</SlideTitle>
		<!-- <ul class="display-small text-error/80 mt-5 list-inside">
			<li>Anywhere / Anytime</li>
			<li>Personal</li>
			<li>Flexible Delivery</li>
			<li>Student Ownership</li>
		</ul> -->
		<div class="fragment grid grid-cols-2 gap-2 pt-20">
			<ChatBubble variant="error" tailAngle={130} shadow={true}>
				<div class="heading-large">Save society for waste of time!</div>
			</ChatBubble>
			<ChatBubble variant="error" tailAngle={350} shadow={true}>
				<div class="heading-large">A great way of learning is by teaching others!</div>
			</ChatBubble>
		</div>
	</FramedSlide>
	<section>
		<div class="r-strech">
			<Display><div class="text-warning">Design<br />(2020 - 2023)</div></Display>
		</div>
	</section>
	<FramedSlide section="old" content={['automation', 'design']}>
		<SlideTitle color="secondary">Presenting same content in different way:</SlideTitle>
		<ul class="display-small text-warning/80 mt-5 list-inside">
			<li>2020: digitized slides</li>
			<li>2021: video recordings and quizzes</li>
			<li>2022: webpresentation I</li>
			<li>2023: webpresentation II</li>
		</ul>
	</FramedSlide>
	<FramedSlide section="old" content={['automation', 'design']}>
		<iframe
			title="Teaching Adventures - Design"
			src="/teachingengagement/teaching-adventures-2023-06.pdf"
			class="shadow-error h-full w-full rounded-4xl object-contain shadow-lg"
		>
		</iframe>
	</FramedSlide>
	<FramedSlide section="old" content={['automation', 'design']}>
		<SlideTitle color="secondary"
			>Compared to other courses at DTU, how do you like the setup in this course inside DTU Learn?</SlideTitle
		>
		<DivergingStackedChart
			data={learnSetupData}
			categories={learnCategories}
			colorClasses={sentimentColors}
			color="warning"
		/>
	</FramedSlide>
	<FramedSlide section="old" content={['automation', 'design']}>
		<SlideTitle color="warning">My attitude towards the students</SlideTitle>

		<div class=" grid grid-cols-2 gap-4 pt-20">
			<ChatBubble variant="warning" tailAngle={130} shadow={true}>
				<div class="heading-large">You never disturb, you always contribute!</div>
			</ChatBubble>
			<ChatBubble variant="warning" tailAngle={210} shadow={true}>
				<div class="heading-large">I started taking courses myself again.</div>
			</ChatBubble>
			<div class="col-span-2 pt-20">
				<ChatBubble variant="warning" tailAngle={305} shadow={true}>
					<div class="heading-large">
						I don't know how you could cheat in my course, use each other and any tool available to
						you - just like in a normal engineering job!
					</div>
				</ChatBubble>
			</div>
		</div>
	</FramedSlide>
	<section>
		<div class="r-strech">
			<Display><div class="text-primary">No Exam<br />(2023 - now)</div></Display>
		</div>
	</section>
	<section>
		<div class="r-strech">
			<Display><div class="text-neutral">Theory</div></Display>
		</div>
	</section>
	<FramedSlide section="new" content={['motivation', '', '', '']}>
		<SlideTitle color="neutral">Talking with the Dean Lars Christoffersen</SlideTitle>
		<ul class="display-small text-neutral/80 mt-5 list-inside">
			<li class="fragment">"Let's get rid of exams!"</li>
			<li class="fragment">building on DTU's honor code</li>
			<!-- <li class="fragment">Theory: "Self Determination Theory - Ib Ravn"</li>
			<li class="fragment">Inspiration: "Mærk Verden - Tor Nørretranders"</li> -->
		</ul>
		<div class="flex w-3/4 justify-around">
			<img
				src="https://hansreitzel.dk/-/media/images/external.png?ei=https://multimediaserver.gyldendal.dk/HansReitzelred/CoverFace/WH_Original/9788741274461&w=320"
				alt="Self determination theory - book cover"
				class="shadow-primary fragment h-fit w-fit rounded-4xl object-contain shadow-lg"
			/>
			<img
				src="https://multimediaserver.gyldendal.dk/GyldendalDk/CoverFace/W200/9788702180602"
				alt="Self determination theory - book cover"
				class="shadow-primary fragment h-full w-fit rounded-4xl object-contain shadow-lg"
			/>
		</div>
		<!-- https://hansreitzel.dk/-/media/images/external.png?ei= -->
	</FramedSlide>
	<FramedSlide section="new" content={['motivation', '', '', '']}>
		<SlideTitle color="neutral">Self determination theory</SlideTitle>
		<div class="mx-5 grid h-120 grid-cols-3 gap-10">
			<div class="heading-large text-neutral flex flex-col">
				<div>Relatedness</div>
				<div
					class="btn btn-neutral-container btn-gradient shadow-outline heading flex h-full flex-col rounded-4xl shadow-sm"
				>
					Your sense of belonging to a community and connection with other people to care for and
					feeling cared for.
				</div>
			</div>
			<div class="heading-large text-neutral flex flex-col">
				<div>Autonomy</div>
				<div
					class="btn btn-neutral-container btn-gradient shadow-outline heading flex h-full flex-col rounded-4xl shadow-sm"
				>
					Making your own decisions about your own life behaviours and goals.
				</div>
			</div>
			<div class="heading-large text-neutral flex flex-col">
				<div>Competence</div>
				<div
					class="btn btn-neutral-container btn-gradient shadow-outline heading flex h-full flex-col rounded-4xl shadow-sm"
				>
					Gaining mastery of your own live and environment to build self-esteem.
				</div>
			</div>

			<!-- <div class="heading-large fragment flex flex-col">
				<div>(Meaning)</div>
				<div
					class="btn btn-info btn-gradient shadow-outline heading flex h-full flex-col rounded-4xl shadow-sm"
				>
					(Feeling your impact on others and your influence to contribute to your environment.)
				</div>
			</div> -->
		</div>
	</FramedSlide>
	<FramedSlide section="new" content={['motivation', '', '', '']}>
		<MotivationTable color="neutral" />
	</FramedSlide>
	<section>
		<div class="r-strech">
			<Display><div class="text-info">Implementation</div></Display>
		</div>
	</section>
	<FramedSlide section="new" content={['motivation', 'implementation', '', '']}>
		<SlideTitle color="neutral">2024</SlideTitle>
		<img
			src="/teachingengagement/grade-reporting-24.png"
			alt="Grade reporting in 2024"
			class="shadow-neutral h-fit w-fit rounded-4xl object-contain shadow-lg"
		/>
	</FramedSlide>
	<FramedSlide section="new" content={['motivation', 'implementation', '', '']}>
		<SlideTitle color="neutral">2025 - now</SlideTitle>
		<img
			src="/teachingengagement/learning-reflection-signals.png"
			alt="Learning reflections in 2025 - now"
			class="shadow-neutral h-fit w-fit rounded-4xl object-contain shadow-lg"
		/>
		<img
			src="/teachingengagement/learning-reflection-components.png"
			alt="Learning reflections in 2025 - now"
			class="shadow-neutral h-fit w-fit rounded-4xl object-contain shadow-lg"
		/>
		<img
			src="/teachingengagement/learning-reflection-circuits.png"
			alt="Learning reflections in 2025 - now"
			class="shadow-neutral h-fit w-fit rounded-4xl object-contain shadow-lg"
		/>
		<img
			src="/teachingengagement/learning-reflection-applications.png"
			alt="Learning reflections in 2025 - now"
			class="shadow-neutral h-fit w-fit rounded-4xl object-contain shadow-lg"
		/>
	</FramedSlide>
	<section>
		<div class="r-strech">
			<Display><div class="text-accent">Results</div></Display>
		</div>
	</section>
	<FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
		<SlideTitle color="accent"
			>Reflecting on my own learning, I learn more, than in a course with exam</SlideTitle
		>
		<DivergingStackedChart
			data={learnedMoreData}
			categories={categoriesNoExam}
			colorClasses={sentimentColors}
			color="accent"
		/>
	</FramedSlide>
	<FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
		<SlideTitle color="accent"
			>Reflecting on my own learning, I take more responsibility for my own learning, than in a
			course with exam</SlideTitle
		>
		<DivergingStackedChart
			data={moreResponsibilityData}
			categories={categoriesNoExam}
			colorClasses={sentimentColors}
			color="accent"
		/>
	</FramedSlide>
	<FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
		<SlideTitle color="accent"
			>Reflecting on my own learning, I can stay more motivated, than in a course with exam</SlideTitle
		>
		<DivergingStackedChart
			data={moreMotivatedData}
			categories={categoriesNoExam}
			colorClasses={sentimentColors}
			color="accent"
		/>
	</FramedSlide>
	<!-- {#if data.questionsData?.goodNoExam}
		<FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
			<SlideTitle color="accent">
				What was <i class="text-success-container-content">good</i> about having the learning reflections
				instead of other exam forms in this course?
			</SlideTitle>
			<QualitativeFeeback color="accent" messages={data.questionsData.goodNoExam.messages} />
		</FramedSlide>
	{/if}
	{#if data.questionsData?.badNoExam}
		<FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
			<SlideTitle color="accent">
				What was <i class="text-error-container">bad</i> about having the learning reflections instead
				of other exam forms in this course?
			</SlideTitle>
			<QualitativeFeeback color="accent" messages={data.questionsData.badNoExam.messages} />
		</FramedSlide>
	{/if} -->
	{#if data.questionsData?.feedback}
		<FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
			<SlideTitle color="accent">Summary of 358 qualitative answers</SlideTitle>
			<!-- <div class="title-large text-accent">
				(<i>208</i> positive, <i>92</i> neutral, <i>58</i> negative)
			</div> -->
			<QualitativeFeeback color="accent" messages={data.questionsData.feedback.messages} />
		</FramedSlide>
	{/if}
	<!-- <FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
		<SlideTitle color="accent">Any comments?</SlideTitle>
		<div class="chat chat-receiver">
			<div class="chat-bubble chat-bubble-accent text-left">
				{@html markdownCommentHtml}
			</div>
		</div>
	</FramedSlide> -->
	<!-- <FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
		<SlideTitle color="accent">Summary of free comments from students</SlideTitle>
		<div class="chat chat-receiver">
			<div class="chat-bubble chat-bubble-accent-container markdown-comment text-left">
				{@html markdownCommentHtml}
			</div>
		</div>
	</FramedSlide> -->
	<!-- {#if data.answer}
		<FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
			<SlideTitle color="accent">Summary of free comments</SlideTitle>
			<div class="chat chat-receiver">
				{#each JSON.parse(data.answer).summaries as finding, idx (idx)}
					<div class="chat-bubble chat-bubble-accent-container markdown-comment text-left">
						{@html marked.parse(finding, { async: false })}
					</div>
				{/each}
			</div>
		</FramedSlide>
	{/if} -->
	<!-- {#if data.questionsData?.comments}
		<FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
			<SlideTitle color="accent">Summary of free comments</SlideTitle>
			<div class="chat chat-receiver">
				{#each data.questionsData.comments.messages as message (message.id)}
					<div class="chat-bubble chat-bubble-accent-container markdown-comment text-left">
						<div class="px-4">
							{@html marked.parse(message.content, { async: false })}
						</div>
					</div>
				{/each}
			</div>
		</FramedSlide>
	{/if} -->
	<!-- {#if data.questionsData?.comments}
		<FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
			<SlideTitle color="accent">Summary of free comments</SlideTitle>
			<QualitativeFeeback color="accent" messages={data.questionsData.comments.messages} />
		</FramedSlide>
	{/if} -->
	<FramedSlide section="new" content={['motivation', 'implementation', 'results', '']}>
		<SlideTitle color="accent">New insights gained</SlideTitle>
		<div class="grid grid-cols-2 gap-2 pt-20">
			<ChatBubble variant="accent" tailAngle={130} shadow={true}>
				<div class="heading-large">No ambitions on other peoples behalf!</div>
			</ChatBubble>
			<ChatBubble variant="accent" tailAngle={190} shadow={true}>
				<div class="heading-large">No "deadlines" ☠️ only "living lines" 🌱.</div>
			</ChatBubble>
			<div class="col-span-2 h-30"></div>
			<ChatBubble variant="accent" tailAngle={30} shadow={true}>
				<div class="heading-large">Who am I to put a number on another person?</div>
			</ChatBubble>
			<ChatBubble variant="accent" tailAngle={330} shadow={true}>
				<div class="heading-large">I only support intrinsic motivation!</div>
			</ChatBubble>
		</div>
	</FramedSlide>
	<section>
		<div class="r-strech">
			<Display><div class="text-primary">Outlook</div></Display>
		</div>
	</section>
	<FramedSlide section="new" content={['motivation', 'implementation', 'results', 'outlook']}>
		<SlideTitle color="primary">CoReLin</SlideTitle>
		<div class="mt-5 grid grid-cols-3 content-center justify-center gap-3">
			<div
				class="btn btn-primary-container btn-gradient shadow-outline heading flex h-50 flex-col rounded-4xl shadow-sm"
			>
				Cocreation
			</div>
			<div
				class="btn btn-primary-container btn-gradient shadow-outline heading flex h-50 flex-col rounded-4xl shadow-sm"
			>
				Reflection
			</div>
			<div
				class="btn btn-primary-container btn-gradient shadow-outline heading flex h-50 flex-col rounded-4xl shadow-sm"
			>
				Learning Intelligence
			</div>
			<div class="flex justify-center py-4">
				<span class="icon-[fa6-solid--arrows-up-down] size-30"></span>
			</div>
			<div class="flex justify-center py-4">
				<span class="icon-[fa6-solid--arrows-up-down] size-30"></span>
			</div>
			<div class="flex justify-center py-4">
				<span class="icon-[fa6-solid--arrows-up-down] size-30"></span>
			</div>
			<div
				class="btn btn-primary-container btn-gradient shadow-outline heading flex h-50 flex-col rounded-4xl shadow-sm"
			>
				Sense of Belonging
			</div>
			<div
				class="btn btn-primary-container btn-gradient shadow-outline heading flex h-50 flex-col rounded-4xl shadow-sm"
			>
				Autonomy
			</div>
			<div
				class="btn btn-primary-container btn-gradient shadow-outline heading flex h-50 flex-col rounded-4xl shadow-sm"
			>
				Competence
			</div>
		</div>
	</FramedSlide>
	<section class="display">
		<Display>Thanks for listening!</Display>
	</section>
	<section class="display">
		<Display>Questions, Reflections, Comments?</Display>
	</section>
</RevealJS>

<style>
	:global(.markdown-comment h1),
	:global(.markdown-comment h2),
	:global(.markdown-comment h3),
	:global(.markdown-comment h4),
	:global(.markdown-comment h5),
	:global(.markdown-comment h6) {
		color: currentColor;
		font-size: inherit;
		font-weight: 700;
		line-height: 1.2;
		margin: 0 0 0.75rem 0;
	}

	:global(.markdown-comment p) {
		margin: 0 0 0.75rem 0;
	}

	:global(.markdown-comment ul) {
		list-style: disc;
		margin: 0 0 0.75rem 1.25rem;
	}

	:global(.markdown-comment a) {
		text-decoration: underline;
	}

	:global(.markdown-comment > :last-child) {
		margin-bottom: 0;
	}
</style>
