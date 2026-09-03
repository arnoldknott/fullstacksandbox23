import { io } from 'socket.io-client';

// Lightweight Socket.IO load generator for the stage backend.
// No browser/rendering: one Node process can hold hundreds of connections.
//
// Usage (question ids are passed as command line arguments, never hard coded):
//   STAGE_BACKEND_URL=https://<backend> bun run test:stage:load -- \
//     --users=50 --hold=30 \
//     /numerical,<motivation-question-id> \
//     /message,<places-question-id>,data \
//     /message,<comments-question-id>,data
//
// Connection spec format: "namespace,parentId[,data]"
//   - namespace: the Socket.IO namespace (e.g. /numerical, /message)
//   - parentId: the parent question id passed as the "parent-id" query param
//   - data: optional literal "data" to send request-access-data=true

const backendUrl = process.env.STAGE_BACKEND_URL?.replace(/\/$/, '');
const socketioPath = '/socketio/v1';

const flags = {};
const connectionSpecs = [];
for (const arg of process.argv.slice(2)) {
	if (arg.startsWith('--')) {
		const [key, value] = arg.slice(2).split('=');
		flags[key] = value ?? 'true';
	} else {
		connectionSpecs.push(arg);
	}
}

const users = Number(flags.users ?? 50);
const holdMs = Number(flags.hold ?? 30) * 1000;

if (!backendUrl) {
	throw new Error('STAGE_BACKEND_URL must be set for the socket.io load test.');
}
if (connectionSpecs.length === 0) {
	throw new Error(
		'Provide at least one connection spec "namespace,parentId[,data]" (e.g. /numerical,<id> /message,<id>,data).'
	);
}

const connections = connectionSpecs.map((spec) => {
	const [namespace, parentId, accessData] = spec.split(',');
	return { namespace, parentId, requestAccessData: accessData === 'data' };
});

let connected = 0;
const errors = [];

const openSocket = ({ namespace, parentId, requestAccessData }, userIndex) => {
	const query = {};
	if (parentId) query['parent-id'] = parentId;
	if (requestAccessData) query['request-access-data'] = 'true';

	const socket = io(backendUrl + namespace, {
		path: socketioPath,
		query,
		transports: ['websocket'],
		forceNew: true
	});

	socket.on('connect', () => connected++);
	socket.on('connect_error', (error) =>
		errors.push(`user ${userIndex} ${namespace} connect_error: ${error.message}`)
	);
	return socket;
}

const oneUser = async (userIndex) => {
	const sockets = connections.map((connection) => openSocket(connection, userIndex));
	await new Promise((resolve) => setTimeout(resolve, holdMs));
	sockets.forEach((socket) => socket.disconnect());
}

const expected = users * connections.length;
console.log(
	`socketio load: ${users} users × ${connections.length} connections = ${expected} sockets against ${backendUrl}`
);

await Promise.all(Array.from({ length: users }, (_, index) => oneUser(index)));

console.log(`socketio load: ${connected}/${expected} connected, ${errors.length} errors`);
errors.slice(0, 20).forEach((error) => console.log(`  ${error}`));
