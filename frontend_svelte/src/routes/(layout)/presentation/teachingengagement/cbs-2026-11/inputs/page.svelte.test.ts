import '@testing-library/jest-dom/vitest';

import { cleanup, fireEvent, render, screen } from '@testing-library/svelte';
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';

import { goto } from '$app/navigation';
import { page } from '$app/state';
import type { QuestionExtended } from '$lib/types';

import InputsPage from './+page.svelte';
import type { PageData } from './$types';

const mock = vi.hoisted(() => ({
	state: undefined as { entities: QuestionExtended[] } | undefined,
	configurations: [] as Array<{ submitOnly?: boolean; snapshot?: unknown }>,
	submitted: vi.fn()
}));
const floatingMock = vi.hoisted(() => ({
	resolvePosition: undefined as ((position: { x: number; y: number }) => void) | undefined,
	cleanup: vi.fn(),
	options: undefined as { animationFrame?: boolean } | undefined
}));

vi.mock('$app/state', async () => {
	const { SvelteURL } = await import('svelte/reactivity');
	return {
		page: {
			url: new SvelteURL(
				'https://example.org/presentation/test/inputs?input=cbs-comments&debug=true'
			)
		}
	};
});
vi.mock('$app/navigation', () => ({
	goto: vi.fn(async (url: URL) => {
		const { page } = await import('$app/state');
		page.url.href = url.href;
	})
}));
vi.mock('svelte/transition', () => ({
	fly: () => ({ duration: 0 }),
	slide: () => ({ duration: 0 })
}));
vi.mock('svelte/animate', () => ({ flip: () => ({ duration: 0 }) }));
vi.mock('$lib/userInterface', () => ({ initTooltip: vi.fn() }));
vi.mock('emoji-picker-element', () => ({}));
vi.mock('@floating-ui/dom', () => ({
	autoUpdate: vi.fn(
		(
			_reference: Element,
			_floating: Element,
			update: () => void,
			options: { animationFrame?: boolean }
		) => {
			floatingMock.options = options;
			update();
			return floatingMock.cleanup;
		}
	),
	computePosition: vi.fn(
		() =>
			new Promise<{ x: number; y: number }>((resolve) => {
				floatingMock.resolvePosition = resolve;
			})
	),
	flip: vi.fn(() => ({})),
	offset: vi.fn(() => ({})),
	shift: vi.fn(() => ({}))
}));
vi.mock('$lib/socketio.svelte', () => ({
	SocketIO: class {
		entities = $state<QuestionExtended[]>([]);
		pendingEntities = [{ id: 'new_message', content: '', confidential: '' }];
		client = { on: vi.fn(), disconnect: vi.fn() };
		constructor(
			connection: { namespace: string },
			configuration: { snapshot?: { entities: QuestionExtended[] }; submitOnly?: boolean }
		) {
			mock.configurations.push(configuration);
			this.entities = configuration.snapshot?.entities ?? [];
			if (connection.namespace === '/question') mock.state = this;
		}
		addPendingAccessPolicy = vi.fn();
		submitEntity(pending: { content: string; confidential: string }, parentId: string) {
			mock.submitted({ ...pending }, parentId);
		}
		createPending() {
			this.pendingEntities = [{ id: 'new_message', content: '', confidential: '' }];
		}
	}
}));

function renderInputs(stateQuestion = 'cbs-presentation-state-comments') {
	const question = {
		id: 'state-question',
		question: stateQuestion,
		language: 'en'
	} as QuestionExtended;
	return render(InputsPage, {
		data: {
			presentationUrl: '/presentation/test',
			inputQuestions: {
				'cbs-names': 'names-question',
				'cbs-places': 'map-question',
				'cbs-books': 'books-question',
				'cbs-comments': 'comments-question'
			},
			stateSnapshot: { entities: [question], cursor: 42 }
		} as unknown as PageData
	});
}

beforeEach(() => {
	mock.state = undefined;
	mock.configurations = [];
	mock.submitted.mockClear();
	floatingMock.resolvePosition = undefined;
	floatingMock.cleanup.mockClear();
	floatingMock.options = undefined;
	vi.mocked(goto).mockClear();
	page.url.href = 'https://example.org/presentation/test/inputs?input=cbs-comments&debug=true';
	Object.defineProperty(Element.prototype, 'getAnimations', {
		configurable: true,
		value: () => []
	});
	vi.stubGlobal(
		'ResizeObserver',
		class {
			observe() {}
			disconnect() {}
		}
	);
});

afterEach(() => {
	cleanup();
	vi.unstubAllGlobals();
});

describe('Mobile inputs page', () => {
	test('submits a name once to cbs-names, only in the confidential attribute', async () => {
		page.url.searchParams.set('input', 'cbs-names');
		renderInputs('cbs-presentation-state-names');
		await fireEvent.input(screen.getByLabelText('Name:'), { target: { value: ' Alex ' } });
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		expect(mock.submitted).toHaveBeenCalledExactlyOnceWith(
			expect.objectContaining({ content: '', confidential: 'Alex' }),
			'names-question'
		);
		expect(screen.queryByRole('button', { name: 'Continue' })).not.toBeInTheDocument();
		expect(screen.getByRole('button', { name: 'Next input' })).toBeDisabled();
		await fireEvent.click(screen.getByRole('button', { name: 'Change your name' }));
		expect(screen.getByLabelText('Name:')).toHaveValue(' Alex ');
		await fireEvent.click(screen.getByRole('button', { name: 'Change your name' }));
		expect(screen.queryByRole('button', { name: 'Continue' })).not.toBeInTheDocument();
		await fireEvent.click(screen.getByRole('button', { name: 'Change your name' }));
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		expect(mock.submitted).toHaveBeenCalledOnce();
	});

	test('anonymous participants skip the names answer on the initial names step', async () => {
		page.url.searchParams.set('input', 'cbs-names');
		renderInputs('cbs-presentation-state-names');
		await fireEvent.input(screen.getByLabelText('Name:'), { target: { value: '   ' } });
		expect(screen.queryByRole('checkbox', { name: 'Anonymous' })).not.toBeInTheDocument();
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		expect(mock.submitted).not.toHaveBeenCalled();
		expect(screen.getByText(/\bAnonymous$/)).toBeInTheDocument();
		expect(screen.queryByRole('button', { name: 'Continue' })).not.toBeInTheDocument();
	});

	test('opens the real map popup and submits a place with its name only in confidential', async () => {
		page.url.searchParams.set('input', 'cbs-places');
		const view = renderInputs();
		await fireEvent.input(screen.getByLabelText('Name:'), { target: { value: 'Alex' } });
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		await vi.waitFor(() =>
			expect(view.container.querySelector('.leaflet-container')).not.toBeNull()
		);
		await fireEvent.click(view.container.querySelector('.leaflet-container')!, {
			clientX: 100,
			clientY: 100
		});
		const textarea = await screen.findByLabelText('How do you connect to this place?');
		const emojiButton = screen.getByRole('button', { name: 'Emoji Picker' });
		const popover = document.getElementById(emojiButton.getAttribute('popovertarget')!)!;
		expect(popover).toHaveAttribute('popover', 'auto');
		expect(emojiButton).toHaveAttribute('type', 'button');
		expect(popover).toHaveClass('invisible');
		const toggleEvent = new Event('toggle');
		Object.defineProperty(toggleEvent, 'newState', { value: 'open' });
		popover.dispatchEvent(toggleEvent);
		expect(floatingMock.options).toEqual({ animationFrame: true });
		expect(popover).toHaveClass('invisible');
		floatingMock.resolvePosition?.({ x: 123, y: 234 });
		await vi.waitFor(() => expect(popover).not.toHaveClass('invisible'));
		expect(popover.style.left).toBe('123px');
		expect(popover.style.top).toBe('234px');
		const hidePopover = vi.fn();
		Object.defineProperty(popover, 'hidePopover', { value: hidePopover, configurable: true });
		popover.querySelector('emoji-picker')!.dispatchEvent(
			new CustomEvent('emoji-click', {
				bubbles: true,
				detail: { unicode: '🌍' }
			})
		);
		await vi.waitFor(() => expect(emojiButton).toHaveTextContent('🌍'));
		expect(hidePopover).toHaveBeenCalledOnce();
		expect(screen.getByLabelText('Name:')).toHaveValue('Alex');
		await fireEvent.input(textarea, { target: { value: 'My home town' } });
		await fireEvent.click(screen.getByRole('button', { name: 'Send' }));
		expect(mock.submitted).toHaveBeenLastCalledWith(
			expect.objectContaining({ confidential: 'Alex' }),
			'map-question'
		);
		const content = JSON.parse(mock.submitted.mock.lastCall![0].content);
		expect(content).toEqual({
			emoji: '🌍',
			text: 'My home town',
			coords: { lat: expect.any(Number), lng: expect.any(Number) }
		});
		expect(content).not.toHaveProperty('name');
		expect(content).not.toHaveProperty('marker');
	});

	test('asks once and reuses the name across comment and book submissions', async () => {
		renderInputs();
		await fireEvent.input(screen.getByLabelText('Name:'), { target: { value: 'Alex' } });
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		expect(screen.queryByRole('button', { name: 'Continue' })).not.toBeInTheDocument();
		await fireEvent.input(screen.getByRole('textbox', { name: /comments or questions/ }), {
			target: { value: 'My question' }
		});
		await fireEvent.click(screen.getByRole('button', { name: 'Send' }));
		expect(mock.submitted).toHaveBeenLastCalledWith(
			expect.objectContaining({ content: 'My question', confidential: 'Alex' }),
			'comments-question'
		);
		await fireEvent.click(screen.getByRole('button', { name: 'Previous input' }));
		await vi.waitFor(() => expect(page.url.searchParams.get('input')).toBe('cbs-books'));
		expect(screen.getByLabelText('Name:')).toHaveValue('Alex');
		await fireEvent.input(screen.getByRole('textbox', { name: /take on this book/ }), {
			target: { value: 'My take' }
		});
		await fireEvent.click(screen.getByRole('button', { name: 'Send' }));
		expect(mock.submitted).toHaveBeenLastCalledWith(
			expect.objectContaining({
				confidential: 'Alex',
				content: JSON.stringify({ bookdid: 'selvbestemmelsesteorien', comment: 'My take' })
			}),
			'books-question'
		);
		expect(
			mock.configurations.find((configuration) => configuration.submitOnly)
		).not.toHaveProperty('snapshot');
		await fireEvent.click(screen.getByRole('button', { name: 'Change your name' }));
		await fireEvent.input(screen.getByLabelText('Name:'), { target: { value: '' } });
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		expect(screen.getByLabelText('Name:')).toHaveValue('');
	});

	test('anonymous choice stops prompting and can be changed from the user icon', async () => {
		renderInputs();
		expect(screen.queryByRole('checkbox', { name: 'Anonymous' })).not.toBeInTheDocument();
		expect(screen.getByLabelText('Name:')).toHaveValue('');
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		expect(mock.submitted).not.toHaveBeenCalled();
		await fireEvent.input(screen.getByRole('textbox', { name: /comments or questions/ }), {
			target: { value: 'Anonymous comment' }
		});
		await fireEvent.click(screen.getByRole('button', { name: 'Send' }));
		expect(mock.submitted).toHaveBeenLastCalledWith(
			expect.objectContaining({ confidential: 'Anonymous' }),
			'comments-question'
		);
		await fireEvent.click(screen.getByRole('button', { name: 'Change your name' }));
		await fireEvent.input(screen.getByLabelText('Name:'), { target: { value: 'Sam' } });
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		expect(screen.getByLabelText('Name:')).toHaveValue('Sam');
	});

	test.each(['names', 'places', 'books', 'comments'])(
		'opens comments manually during the %s step and cancels without submitting or navigating',
		async (step) => {
			page.url.searchParams.set('input', `cbs-${step}`);
			renderInputs(`cbs-presentation-state-${step}`);
			await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
			const originalUrl = page.url.href;
			expect(screen.getByRole('main')).toBeInTheDocument();
			expect(screen.queryByRole('button', { name: 'Cancel' })).not.toBeInTheDocument();

			await fireEvent.click(
				screen.getByRole('button', { name: 'Ask a question or leave a comment' })
			);
			expect(screen.queryByRole('main')).not.toBeInTheDocument();
			const commentInput = screen.getByRole('textbox', { name: /comments or questions/ });
			await fireEvent.input(commentInput, { target: { value: 'My draft question' } });
			expect(screen.getByRole('button', { name: 'Cancel' })).toHaveAttribute('type', 'button');
			await fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));

			expect(screen.getByRole('main')).toBeInTheDocument();
			expect(screen.queryByRole('button', { name: 'Cancel' })).not.toBeInTheDocument();
			expect(mock.submitted).not.toHaveBeenCalled();
			expect(page.url.href).toBe(originalUrl);
			await fireEvent.click(
				screen.getByRole('button', { name: 'Ask a question or leave a comment' })
			);
			expect(screen.getByRole('textbox', { name: /comments or questions/ })).toHaveValue(
				'My draft question'
			);
			await fireEvent.click(
				screen.getByRole('button', { name: 'Ask a question or leave a comment' })
			);
			expect(screen.getByRole('main')).toBeInTheDocument();
			expect(screen.queryByRole('button', { name: 'Cancel' })).not.toBeInTheDocument();
		}
	);

	test('submits a manual question before the comments step using the participant name', async () => {
		page.url.searchParams.set('input', 'cbs-books');
		renderInputs('cbs-presentation-state-books');
		await fireEvent.input(screen.getByLabelText('Name:'), { target: { value: 'Alex' } });
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		mock.submitted.mockClear();
		await fireEvent.click(
			screen.getByRole('button', { name: 'Ask a question or leave a comment' })
		);
		expect(screen.getByLabelText('Name:')).toHaveValue('Alex');
		expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled();
		await fireEvent.input(screen.getByRole('textbox', { name: /comments or questions/ }), {
			target: { value: 'My early question' }
		});
		await fireEvent.click(screen.getByRole('button', { name: 'Send' }));
		expect(mock.submitted).toHaveBeenCalledExactlyOnceWith(
			expect.objectContaining({ content: 'My early question', confidential: 'Alex' }),
			'comments-question'
		);
		expect(screen.getByRole('textbox', { name: /comments or questions/ })).toHaveValue('');
		expect(screen.getByRole('status')).toHaveTextContent('Sending...');
		await fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
		expect(screen.getByRole('textbox', { name: /take on this book/ })).toBeInTheDocument();
		expect(page.url.searchParams.get('input')).toBe('cbs-books');
	});

	test('the initial and reopened name forms take precedence over manual comments', async () => {
		page.url.searchParams.set('input', 'cbs-names');
		renderInputs('cbs-presentation-state-names');
		await fireEvent.click(
			screen.getByRole('button', { name: 'Ask a question or leave a comment' })
		);
		expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();
		expect(
			screen.queryByRole('textbox', { name: /comments or questions/ })
		).not.toBeInTheDocument();
		expect(screen.queryByRole('button', { name: 'Cancel' })).not.toBeInTheDocument();
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		await fireEvent.input(screen.getByRole('textbox', { name: /comments or questions/ }), {
			target: { value: 'My draft question' }
		});

		await fireEvent.click(screen.getByRole('button', { name: 'Change your name' }));
		expect(screen.getByRole('button', { name: 'Continue' })).toBeInTheDocument();
		expect(
			screen.queryByRole('textbox', { name: /comments or questions/ })
		).not.toBeInTheDocument();
		expect(screen.queryByRole('button', { name: 'Cancel' })).not.toBeInTheDocument();
		await fireEvent.input(screen.getByLabelText('Name:'), { target: { value: 'Sam' } });
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		expect(screen.getByLabelText('Name:')).toHaveValue('Sam');
		expect(screen.getByRole('textbox', { name: /comments or questions/ })).toHaveValue(
			'My draft question'
		);
		expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
		await fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
		expect(screen.getByText('Welcome Sam')).toBeInTheDocument();
	});

	test('manual comments stay open during live state changes and cancel returns to the current step', async () => {
		page.url.searchParams.set('input', 'cbs-names');
		renderInputs('cbs-presentation-state-names');
		await fireEvent.click(screen.getByRole('button', { name: 'Continue' }));
		await fireEvent.click(
			screen.getByRole('button', { name: 'Ask a question or leave a comment' })
		);
		await fireEvent.input(screen.getByRole('textbox', { name: /comments or questions/ }), {
			target: { value: 'My draft question' }
		});
		mock.state!.entities = [
			{ ...mock.state!.entities[0], question: 'cbs-presentation-state-comments' }
		];
		await vi.waitFor(() => expect(page.url.searchParams.get('input')).toBe('cbs-comments'));
		expect(screen.getByRole('textbox', { name: /comments or questions/ })).toHaveValue(
			'My draft question'
		);
		expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument();
		await fireEvent.click(screen.getByRole('button', { name: 'Cancel' }));
		expect(screen.getByRole('main')).toBeInTheDocument();
		expect(screen.getByRole('textbox', { name: /comments or questions/ })).toHaveValue(
			'My draft question'
		);
		expect(screen.queryByRole('button', { name: 'Cancel' })).not.toBeInTheDocument();
		expect(mock.submitted).not.toHaveBeenCalled();
	});

	test('live state changes update the query while preserving other parameters', async () => {
		renderInputs();
		await vi.waitFor(() => expect(mock.state).toBeDefined());
		mock.state!.entities = [
			{ ...mock.state!.entities[0], question: 'cbs-presentation-state-books' }
		];
		await vi.waitFor(() => expect(page.url.searchParams.get('input')).toBe('cbs-books'));
		expect(page.url.searchParams.get('debug')).toBe('true');
		expect(goto).toHaveBeenCalledWith(expect.any(URL), {
			replaceState: true,
			noScroll: true,
			keepFocus: true
		});
		expect(screen.getByText('Book', { selector: '.title' })).toBeInTheDocument();
		expect(screen.getByRole('button', { name: 'Next input' })).toBeDisabled();
		mock.state!.entities = [
			{ ...mock.state!.entities[0], question: 'cbs-presentation-state-comments' }
		];
		await vi.waitFor(() => expect(page.url.searchParams.get('input')).toBe('cbs-comments'));
		expect(screen.getByRole('button', { name: 'Next input' })).toBeDisabled();
		await fireEvent.click(screen.getByRole('button', { name: 'Next input' }));
		expect(page.url.searchParams.get('input')).toBe('cbs-comments');
	});

	test('replaces an obsolete link selection with the current input and keeps the footer link', async () => {
		page.url.searchParams.set('input', 'link');
		renderInputs();
		await vi.waitFor(() => expect(page.url.searchParams.get('input')).toBe('cbs-comments'));
		expect(screen.getByRole('link', { name: /Presentation/ })).toHaveAttribute(
			'href',
			'/presentation/test'
		);
	});
});
