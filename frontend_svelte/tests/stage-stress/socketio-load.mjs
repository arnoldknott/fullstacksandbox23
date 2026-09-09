import { io } from 'socket.io-client';

// Fixed load scenario for the 34654/e26/introduction presentation.
// No browser/rendering: frontend mode requests the SvelteKit page and discards
// its HTML; backend mode loads the REST data and holds the presentation sockets.
//
// Modes:
//   - no mode flag: frontend preload plus backend Socket.IO connections
//   - --frontend-only: frontend preload only
//   - --backend-only: backend REST preload plus Socket.IO connections
//
// Usage:
//   STAGE_FRONTEND_URL=https://<frontend> STAGE_BACKEND_URL=https://<backend> \
//     bun run test:stage:load -- --users=50 --hold=30 --timeout=120

const frontendRoute = '/presentation/34654/e26/introduction';
const presentationPath = '34654/e26/introduction';
const frontendUrl = process.env.STAGE_FRONTEND_URL?.replace(/\/$/, '');
const backendUrl = process.env.STAGE_BACKEND_URL?.replace(/\/$/, '');
const socketioPath = '/socketio/v1';

const flags = {};
const supportedFlags = new Set(['users', 'hold', 'timeout', 'frontend-only', 'backend-only']);
for (const arg of process.argv.slice(2)) {
	if (!arg.startsWith('--')) {
		throw new Error(`Unknown positional argument: ${arg}`);
	}
	const separatorIndex = arg.indexOf('=');
	const key = arg.slice(2, separatorIndex === -1 ? undefined : separatorIndex);
	if (!supportedFlags.has(key)) {
		throw new Error(`Unknown option: --${key}`);
	}
	flags[key] = separatorIndex === -1 ? 'true' : arg.slice(separatorIndex + 1);
}

const users = Number(flags.users ?? 50);
const holdMs = Number(flags.hold ?? 30) * 1000;
const timeoutMs = Number(flags.timeout ?? 120) * 1000;
const frontendOnly = flags['frontend-only'] === 'true';
const backendOnly = flags['backend-only'] === 'true';
const runFrontend = !backendOnly;
const runBackend = !frontendOnly;

if (frontendOnly && backendOnly) {
	throw new Error('Choose only one of --frontend-only or --backend-only.');
}
if (runFrontend && !frontendUrl) {
	throw new Error('STAGE_FRONTEND_URL must be set for frontend load testing.');
}
if (runBackend && !backendUrl) {
	throw new Error('STAGE_BACKEND_URL must be set for backend load testing.');
}
if (!Number.isSafeInteger(users) || users < 1) {
	throw new Error('--users must be a positive integer.');
}
if (!Number.isFinite(holdMs) || holdMs < 0) {
	throw new Error('--hold must be a non-negative number of seconds.');
}
if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
	throw new Error('--timeout must be a positive number of seconds.');
}

const fetchBodyWithTimeout = async (url, label) => {
	const controller = new AbortController();
	const timer = setTimeout(() => controller.abort(), timeoutMs);
	try {
		const response = await fetch(url, { signal: controller.signal });
		const body = await response.arrayBuffer();
		return { response, body };
	} catch (error) {
		if (controller.signal.aborted) {
			throw new Error(`${label} timed out after ${timeoutMs / 1000}s`, { cause: error });
		}
		throw error;
	} finally {
		clearTimeout(timer);
	}
};

const discoverPresentationConnections = async () => {
	const discoveryUrl = new URL(`/api/v1/presentation/path/${presentationPath}`, `${backendUrl}/`);
	const { response, body } = await fetchBodyWithTimeout(discoveryUrl, 'Presentation discovery');
	if (!response.ok) {
		throw new Error(`Presentation discovery returned HTTP ${response.status}.`);
	}

	const presentation = JSON.parse(new TextDecoder().decode(body));
	const findQuestionId = (text) => {
		const question = presentation.questions?.find((candidate) =>
			candidate.question?.includes(text)
		);
		if (!question?.id) {
			throw new Error(`Presentation has no question containing "${text}".`);
		}
		return question.id;
	};

	return [
		{
			namespace: '/numerical',
			parentId: findQuestionId('motivation'),
			requestAccessData: false
		},
		{
			namespace: '/message',
			parentId: findQuestionId('places'),
			requestAccessData: true
		},
		{
			namespace: '/message',
			parentId: findQuestionId('comments'),
			requestAccessData: true
		}
	];
};

const connections = runBackend ? await discoverPresentationConnections() : [];
let preloaded = 0;
let connected = 0;
const errors = [];

const preloadFrontendPage = async (userIndex) => {
	const { response } = await fetchBodyWithTimeout(
		new URL(frontendRoute, frontendUrl),
		`user ${userIndex} frontend preload`
	);
	if (!response.ok) {
		throw new Error(`user ${userIndex} frontend preload returned HTTP ${response.status}`);
	}
	preloaded++;
};

const preloadBackendData = async (userIndex) => {
	const snapshotPaths = connections.map(
		({ namespace, parentId }) =>
			`/api/v1/quiz/${namespace.slice(1)}/snapshot?parent-id=${encodeURIComponent(parentId)}&include=creation-date&sort=creation-date&direction=desc`
	);
	const paths = [`/api/v1/presentation/path/${presentationPath}`, ...snapshotPaths];
	const responses = await Promise.all(
		paths.map((path) =>
			fetchBodyWithTimeout(new URL(path, `${backendUrl}/`), `user ${userIndex} backend preload`)
		)
	);
	const failedIndex = responses.findIndex(({ response }) => !response.ok);
	if (failedIndex !== -1) {
		const failed = responses[failedIndex];
		const body = new TextDecoder().decode(failed.body).slice(0, 500);
		throw new Error(
			`user ${userIndex} backend preload ${paths[failedIndex]} returned HTTP ${failed.response.status}: ${body}`
		);
	}
	preloaded++;
};

const openSocket = ({ namespace, parentId, requestAccessData }, userIndex) => {
	const query = { 'parent-id': parentId };
	if (requestAccessData) query['request-access-data'] = 'true';

	const socket = io(backendUrl + namespace, {
		path: socketioPath,
		query,
		transports: ['websocket'],
		forceNew: true,
		timeout: timeoutMs,
		reconnection: false
	});
	const ready = new Promise((resolve, reject) => {
		const timer = setTimeout(() => {
			const message =
				'user ' + userIndex + ' ' + namespace + ' connect timeout after ' + timeoutMs / 1000 + 's';
			errors.push(message);
			socket.disconnect();
			reject(new Error(message));
		}, timeoutMs);
		socket.once('connect', () => {
			connected++;
			clearTimeout(timer);
			resolve();
		});
		socket.once('connect_error', (error) => {
			clearTimeout(timer);
			const message = `user ${userIndex} ${namespace} connect_error: ${error.message}`;
			errors.push(message);
			reject(new Error(message));
		});
	});

	return { socket, ready };
};

const oneUser = async (userIndex) => {
	try {
		if (runFrontend) {
			await preloadFrontendPage(userIndex);
		}
		if (backendOnly) {
			await preloadBackendData(userIndex);
		}
	} catch (error) {
		errors.push(error instanceof Error ? error.message : `user ${userIndex} preload failed`);
		return;
	}

	if (!runBackend) return;

	const clients = connections.map((connection) => openSocket(connection, userIndex));
	await Promise.allSettled(clients.map(({ ready }) => ready));
	await new Promise((resolve) => setTimeout(resolve, holdMs));
	clients.forEach(({ socket }) => socket.disconnect());
};

const expectedSockets = runBackend ? users * connections.length : 0;
const targetUrl = runBackend ? backendUrl : frontendUrl;
const mode = frontendOnly ? 'frontend-only' : backendOnly ? 'backend-only' : 'frontend + backend';
console.log(
	`stage load (${mode}): ${users} users × ${expectedSockets} sockets against ${targetUrl}`
);
if (runFrontend) {
	console.log(`stage load: each user preloads ${new URL(frontendRoute, frontendUrl)}`);
}
if (backendOnly) {
	console.log('stage load: each user also preloads backend REST data directly');
}

const progressTimer = setInterval(
	() =>
		console.log(
			'stage load progress: preloads ' +
				preloaded +
				'/' +
				users +
				', sockets ' +
				connected +
				'/' +
				expectedSockets +
				', hold=' +
				holdMs / 1000 +
				's'
		),
	10000
);
await Promise.all(Array.from({ length: users }, (_, index) => oneUser(index)));
clearInterval(progressTimer);

console.log(`stage load: ${preloaded}/${users} preloads succeeded`);
console.log(
	`stage load: ${connected}/${expectedSockets} sockets connected, ${errors.length} errors`
);
errors.slice(0, 20).forEach((error) => console.log(`  ${error}`));

if (errors.length > 0 || preloaded !== users || connected !== expectedSockets) {
	process.exitCode = 1;
}
