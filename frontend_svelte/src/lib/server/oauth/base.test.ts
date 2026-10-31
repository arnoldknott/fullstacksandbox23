import { describe, expect, test, vi } from 'vitest';

import { getRequestEvent } from '$app/server';

import {
	createOAuthTransaction,
	redirectToReauthentication,
	validateOAuthIntent,
	validateOAuthTransaction
} from './base';

vi.mock('$app/server', () => ({ getRequestEvent: vi.fn() }));

describe('reauthentication entry points', () => {
	test.each([
		{ accept: 'text/html', isDataRequest: false, action: 'false' },
		{ accept: '*/*', isDataRequest: true, action: 'false' },
		{ accept: 'application/json', isDataRequest: false, action: 'true' }
	])('redirects page requests while preserving path and query (%j)', (request) => {
		const url = new URL('https://app.example/presentation/cbs?presenter=true');
		vi.mocked(getRequestEvent).mockReturnValue({
			url,
			isDataRequest: request.isDataRequest,
			request: new Request(url, {
				headers: { accept: request.accept, 'x-sveltekit-action': request.action }
			})
		} as never);

		expect(() => redirectToReauthentication()).toThrow(
			expect.objectContaining({
				status: 307,
				location: `/login/microsoft?target-url=${encodeURIComponent(url.href)}`
			})
		);
	});

	test('rejects background requests rather than starting authorization in a fetch', () => {
		const url = new URL('https://app.example/apiproxies/msgraph?endpoint=/me/photo/$value');
		vi.mocked(getRequestEvent).mockReturnValue({
			url,
			isDataRequest: false,
			request: new Request(url)
		} as never);

		expect(() => redirectToReauthentication()).toThrow(expect.objectContaining({ status: 401 }));
	});
});

describe('OAuth transactions', () => {
	test('binds state, intent, data, and an independent expiry', () => {
		const transaction = createOAuthTransaction(
			'state-1',
			'reauthentication',
			600,
			{
				redirectUri: 'https://app.example/oauth/callback',
				targetUrl: '/target',
				parentUrl: 'https://parent.example/'
			},
			1_000
		);

		expect(transaction).toEqual({
			state: 'state-1',
			intent: 'reauthentication',
			expiresAt: 601_000,
			redirectUri: 'https://app.example/oauth/callback',
			targetUrl: '/target',
			parentUrl: 'https://parent.example/'
		});
		expect(validateOAuthTransaction(transaction, 'state-1', 600_999)).toBe(transaction);
	});

	test('rejects expired or mismatched transactions', () => {
		const transaction = createOAuthTransaction(
			'state-1',
			'login',
			10,
			{ redirectUri: 'https://app.example/oauth/callback', targetUrl: '/' },
			1_000
		);

		expect(() => validateOAuthTransaction(transaction, 'state-2', 2_000)).toThrow(
			'OAuth transaction state mismatch.'
		);
		expect(() => validateOAuthTransaction(transaction, 'state-1', 11_000)).toThrow(
			'OAuth transaction expired.'
		);
	});

	test('binds login to pending sessions and reauthentication/link to established sessions', () => {
		expect(() => validateOAuthIntent('login', false)).not.toThrow();
		expect(() => validateOAuthIntent('reauthentication', true)).not.toThrow();
		expect(() => validateOAuthIntent('link', true)).not.toThrow();
		expect(() => validateOAuthIntent('login', true)).toThrow();
		expect(() => validateOAuthIntent('reauthentication', false)).toThrow();
	});
});
