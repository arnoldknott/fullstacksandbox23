// import { browser } from "$app/environment";
// import type { Session } from "$lib/server/session";
// import { getAccessToken } from "./server/oauth";

// const host = `http://${process.env.BACKEND_HOST}:80`;

console.log('Hello from totally redundant backend.ts');

// Seems to be a bit of an overkill and trying to reproduce
// the fetch function available in server load functions
// in server load functions locals is also available, where the sessionData is stored
// so a lib function could be to turn the sessionData into an accessToken.
// Passing an account is required when accessing protected routes in the backend.
// export const getBackend = async (url: string, session: Session | null = null) => {
// 	let accessToken = null;
// 	if(!browser && session){
// 		accessToken = await getAccessToken(session);
// 	}

// 	const headers = {
// 		'Content-Type': 'application/json',
// 		Authorization: `Bearer ${accessToken}`
// 	};
// 	const response = await fetch(host + url, {
// 		method: 'GET',
// 		headers: headers
// 	});
// 	const data = await response.json();
// 	return data;
// };

// // TBD: POST to backend
// export const postBackend = async (url: string, payload: User) => {
// 	const response = await fetch(host + url, {
// 		method: 'POST',
// 		headers: {
// 			'Content-Type': 'application/json'
// 		},
// 		body: JSON.stringify(payload)
// 	});
// 	const data = await response.json();
// 	return data;
// };
// // TBD: PUT to backend
// // TBD: DELETE from backend

// // TBD: write test for getUser
// // export const getUser = async () => {
// //     await getBackend('https://backend/api/user');
// // };
