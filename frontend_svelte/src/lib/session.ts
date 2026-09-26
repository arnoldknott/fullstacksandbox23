import type { Socket } from 'socket.io-client';
import { getContext, setContext } from 'svelte';

import { goto } from '$app/navigation';
import { resolve } from '$app/paths';
import { page } from '$app/state';

import { IdentityProvider, preferredIdentityProvider } from './identityProvider';

const SESSION_LIFECYCLE_KEY = Symbol('session-lifecycle');
const TOUCH_INTERVAL_MS = 5 * 60 * 1000;

export enum SessionStatus {
	AUTHENTICATION_PENDING = 'authentication_pending',
	REGISTRATION_PENDING = 'registration_pending',
	REGISTERED = 'registered'
}

export class SessionLifecycle {
	private lastTouchAttemptAt = 0;
	private touchInFlight?: Promise<void>;
	private reauthenticationStarted = false;

	async touchIfDue(socket?: Socket): Promise<void> {
		if (page.data.session?.loggedIn !== true) return;
		const now = Date.now();
		if (now - this.lastTouchAttemptAt < TOUCH_INTERVAL_MS) return;
		if (this.touchInFlight) return this.touchInFlight;
		this.lastTouchAttemptAt = now;
		this.touchInFlight = fetch(resolve('/session/touch'), {
			method: 'POST',
			headers: { Authorization: `Bearer ${page.data.session.sessionId}` }
		})
			.then((response) => {
				if (response.status === 401 && socket) this.reauthenticate(socket);
			})
			.finally(() => {
				this.touchInFlight = undefined;
			});
		return this.touchInFlight;
	}

	reauthenticate(socket: Socket): void {
		socket.disconnect();
		if (this.reauthenticationStarted) return;
		const provider = preferredIdentityProvider(
			page.data.session?.currentUser ?? {},
			page.data.session?.identityProvider
		);
		if (!provider) {
			throw new Error('Reauthentication required, but no suitable identity provider found.');
		}
		this.reauthenticationStarted = true;
		const targetUrl = encodeURIComponent(window.location.href);
		const path = provider === IdentityProvider.MICROSOFT ? '/login/microsoft' : '/login/linkedin';
		void Promise.resolve(goto(resolve(`${path}?target-url=${targetUrl}`))).catch(() => {
			this.reauthenticationStarted = false;
		});
	}
}

export function setSessionLifecycleContext(): SessionLifecycle {
	const lifecycle = new SessionLifecycle();
	setContext(SESSION_LIFECYCLE_KEY, lifecycle);
	return lifecycle;
}

export function getSessionLifecycleContext(): SessionLifecycle {
	return getContext<SessionLifecycle | undefined>(SESSION_LIFECYCLE_KEY) ?? new SessionLifecycle();
}
