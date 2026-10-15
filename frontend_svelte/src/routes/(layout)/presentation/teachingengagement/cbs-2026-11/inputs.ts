export const presentationStatePrefix = 'cbs-presentation-state-';

export const inputOptions = [
	{ label: 'Name', question: 'cbs-names' },
	{ label: 'Map', question: 'cbs-places' },
	{ label: 'Book', question: 'cbs-books' },
	{ label: 'Comment', question: 'cbs-comments' }
] as const;

export type InputQuestion = (typeof inputOptions)[number]['question'];

export function getInputsUrl(url: URL, input?: string | null): string {
	const inputsUrl = new URL(url);
	const presentationPath = inputsUrl.pathname
		.replace(/\/(?:qrcode|inputs)\/?$/, '')
		.replace(/\/$/, '');
	inputsUrl.pathname = `${presentationPath}/inputs`;
	inputsUrl.search = '';
	inputsUrl.hash = '';
	if (input) inputsUrl.searchParams.set('input', input);
	return inputsUrl.toString();
}

export function currentInput(question?: string): InputQuestion | undefined {
	if (!question?.startsWith(presentationStatePrefix)) return;
	const inputQuestion = `cbs-${question.slice(presentationStatePrefix.length)}`;
	return inputOptions.find((option) => option.question === inputQuestion)?.question;
}

export function inputEnabled(question: string, current?: InputQuestion): boolean {
	const index = inputOptions.findIndex((option) => option.question === question);
	const currentIndex = inputOptions.findIndex((option) => option.question === current);
	return index >= 0 && index <= currentIndex;
}

export function selectedInput(
	requested: string | null,
	current?: InputQuestion
): InputQuestion | undefined {
	if (requested && inputEnabled(requested, current)) return requested as InputQuestion;
	return current;
}
