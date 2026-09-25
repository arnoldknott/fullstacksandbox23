import { describe, expect, test } from 'vitest';

import { createOAuthTransaction, validateOAuthIntent, validateOAuthTransaction } from './base';

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
