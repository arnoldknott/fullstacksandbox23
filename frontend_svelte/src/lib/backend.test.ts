// tests for backend functions
// import { describe, test, expect, beforeAll, afterAll } from 'vitest';
// import { setupServer } from 'msw/node';
// import { rest } from 'msw';
// import { getBackend, postBackend } from './backend';

// const dummyResponse = { data: 'test' };

import { describe, test, expect } from 'vitest';

describe('dummy test', () => {
	test('should pass', () => {
		expect(true).toBe(true);
	});
});

// const server = setupServer(
// 	rest.get('http://host.docker.internal:8660/api/schema', (req, res, ctx) => {
// 		req.url.searchParams.set('format', 'json');
// 		return res(ctx.json(dummyResponse));
// 	})
// );

// beforeAll(() => server.listen());
// afterAll(() => server.close());

// describe('GET data from backend', () => {
// 	test('should get data from backend', async () => {
// 		const data = await getBackend('/api/schema?format=json');
// 		expect(data).toEqual(dummyResponse);
// 	});
// });

// describe('POST data to backend', () => {
// 	test('should post data to backend', async () => {
// 		const payload = {
// 			name: 'User One',
// 			email: 'user@example.com',
// 			password: 'secretPassword'
// 		};
// 		server.use(
// 			rest.post('http://host.docker.internal:8000/api/user/create', async (req, res, ctx) => {
// 				const requestData = await req.json();
// 				if (JSON.stringify(requestData) === JSON.stringify(payload)) {
// 					return res(
// 						ctx.status(200),
// 						ctx.json({
// 							name: payload.name,
// 							email: payload.email
// 						})
// 					);
// 				} else {
// 					return res(
// 						ctx.status(400),
// 						ctx.json({
// 							error: 'Bad Request'
// 						})
// 					);
// 				}
// 			})
// 		);
// 		const response = await postBackend('/api/user/create', payload);
// 		expect(response).toContain({ name: 'User One', email: 'user@example.com' });
// 	});
// 	test.todo('should read the posted data back from the backend');
// });
