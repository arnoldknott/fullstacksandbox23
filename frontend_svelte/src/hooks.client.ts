// import('flyonui/flyonui');
import 'flyonui/flyonui';
window.HSStaticMethods.autoInit();

// import type { HandleFetch } from '@sveltejs/kit';
// export const handleFetch: HandleFetch = async ({ event, request, fetch }) => {
// 	const sessionId = localStorage.getItem('session_id');
// 	console.log('=== hooks.client.ts - handleFetch - sessionId ===');
// 	console.log(sessionId);
// 	// Only add the Authorization header for same-origin requests and if sessionId is available
// 	if (sessionId && request.url.startsWith(event.url.origin)) {
// 		const headers = new Headers(request.headers);
// 		headers.set('Authorization', `Bearer ${sessionId}`);
// 		request = new Request(request, { headers });
// 	}
// 	return fetch(request);
// };

// // Override global fetch to inject Authorization header
// if (typeof window !== 'undefined') {
// 	const originalFetch = window.fetch;

// 	window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
// 		const sessionId = localStorage.getItem('session_id');
// 		console.log('=== hooks.client.ts - fetch override - sessionId ===');
// 		console.log(sessionId);

// 		// Add Authorization header if sessionId exists
// 		if (sessionId) {
// 			const headers = new Headers(init?.headers || {});

// 			// Only add for same-origin requests
// 			const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
// 			if (url.startsWith('/') || url.startsWith(window.location.origin)) {
// 				headers.set('Authorization', `Bearer ${sessionId}`);
// 			}

// 			init = { ...init, headers };
// 		}

// 		return originalFetch(input, init);
// 	};
// }

const native_fetch = window.fetch;

export async function init() {
	// Make the override conditional
	// on the presence of session_id in localStorage
	// to avoid unnecessary overhead when the page is not embedded?
	window.fetch = (request, init) => {
		const sessionId = localStorage.getItem('session_id');
		// console.log('=== hooks.client.ts - fetch override in init() - sessionId ===');
		// console.log(sessionId);
		// Add Authorization header if sessionId exists
		if (sessionId) {
			const headers = new Headers(init?.headers || {});

			// Only add for same-origin requests
			const url =
				typeof request === 'string' ? request : request instanceof URL ? request.href : request.url;
			if (url.startsWith('/') || url.startsWith(window.location.origin)) {
				// console.log(
				// 	'=== hooks.client.ts - fetch override in init() - adding Authorization header ==='
				// );
				headers.set('Authorization', `Bearer ${sessionId}`);
			}

			init = { ...init, headers };
		}
		return native_fetch(request, init);
	};
}
