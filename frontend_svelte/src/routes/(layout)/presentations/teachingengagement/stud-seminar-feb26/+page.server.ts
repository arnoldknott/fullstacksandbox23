import type { PageServerLoad } from './$types';
import { backendAPI } from '$lib/server/apis/backendApi';
import type { Question } from '$lib/types';

export const load: PageServerLoad = async ({ url }) => {
	// const questionGoodNoExamId = url.searchParams.get('q-good-no-exam');
	// const questionBadNoExamId = url.searchParams.get('q-bad-no-exam');
	// const questionCommentsId = url.searchParams.get('q-comments');
	const questionFeedbackId = url.searchParams.get('q-feedback');
	// Stringify an answer:
	// 	const answer = JSON.stringify({
	// 		course: 'dev2',
	// 		year: '2023',
	// 		// summaries: [
	// 		// 	"#Heading\n\nThis is a **markdown** response with _formatting_.\n\n- It supports lists\n- And other markdown features\n\n##A Second heading\n\n[Here's a link](https://www.example.com)"
	// 		// ]
	// 		// summaries: [
	// 		// 	"# Heading This is a **markdown** response with _formatting_. - It supports lists - And other markdown features ## Second heading ### Third Heading [Here's a link](https://www.example.com)"
	// 		// ]
	// 		summaries: [
	// 			`# Heading

	// This is a **markdown** response with _formatting_.

	// - It supports lists
	// - And other markdown features

	// ## Second heading

	// ### Third Heading

	// [Here's a link](https://www.example.com)`
	// 		]
	// 	});
	// 	console.log('=== 🧦 presentation - devF23 - motivation - answer stringified ===');
	// 	console.log(answer);
	// const responseGoodNoExam = await backendAPI.get(
	// 	null,
	// 	'/quiz/question/public/' + questionGoodNoExamId
	// );
	// const responseBadNoExam = await backendAPI.get(
	// 	null,
	// 	'/quiz/question/public/' + questionBadNoExamId
	// );
	// const responseComments = await backendAPI.get(
	// 	null,
	// 	'/quiz/question/public/' + questionCommentsId
	// );
	const responseFeedback = await backendAPI.get(
		null,
		'/quiz/question/public/' + questionFeedbackId
	);
	type QuestionData = {
		// goodNoExam?: Question;
		// badNoExam?: Question;
		// comments?: Question;
		feedback?: Question;
	};
	let questionsData: QuestionData = {
		// goodNoExam: undefined,
		// badNoExam: undefined,
		// comments: undefined,
		feedback: undefined
	};
	// if (responseGoodNoExam.status === 200) {
	// 	const goodNoExamData = await responseGoodNoExam.json();
	// 	if (questionsData) {
	// 		questionsData.goodNoExam = goodNoExamData;
	// 	} else {
	// 		questionsData = { goodNoExam: goodNoExamData };
	// 	}
	// }
	// if (responseBadNoExam.status === 200) {
	// 	const badNoExamData = await responseBadNoExam.json();
	// 	if (questionsData) {
	// 		questionsData.badNoExam = badNoExamData;
	// 	} else {
	// 		questionsData = { badNoExam: badNoExamData };
	// 	}
	// }
	// if (responseComments.status === 200) {
	// 	const commentsData = await responseComments.json();
	// 	if (questionsData) {
	// 		questionsData.comments = commentsData;
	// 	} else {
	// 		questionsData = { comments: commentsData };
	// 	}
	// }
	if (responseFeedback.status === 200) {
		const feedbackData = await responseFeedback.json();
		if (questionsData) {
			questionsData.feedback = feedbackData;
		} else {
			questionsData = { feedback: feedbackData };
		}
	}
	// console.log('=== 🧦 presentation - devF23 - motivation - questionsData loaded ===');
	// console.log(questionsData);
	return { questionsData };
	// return { answer };
};
