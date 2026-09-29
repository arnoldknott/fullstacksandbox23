import { error, json } from '@sveltejs/kit';

import { backendAPI } from '$lib/server/apis/backendApi';

import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ locals }) => {
	const sessionId = locals.sessionData.sessionId;
	const response = await backendAPI.post(sessionId, '/core/socketio-ticket', '{}');
	if (!response.ok) error(response.status, 'Socket.IO admission ticket could not be created');
	return json(await response.json());
};
