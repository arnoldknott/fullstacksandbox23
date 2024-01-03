// handle the backend API calls
// import type { User } from 'src/types.d.ts';

import { getAccessToken } from "./oauth";

// const host = 'http://host.docker.internal:8000';
// const host = 'http://backend_api:80';
// import dotenv from 'dotenv';
// dotenv.config();

// console.log('process.env.BACKEND_HOST: ', process.env.BACKEND_HOST);
const host = `http://${process.env.BACKEND_HOST}:80`;


export const getBackend = async (url: string) => {
	const accessToken = await getAccessToken();
	const headers = {
		'Content-Type': 'application/json',
		Authorization: `Bearer ${accessToken}` 
	};
	// accessToken = sessionStorage.getItem('accessToken') || '';
	// if (accessToken) {
	// 	headers.Authorization = `Bearer ${accessToken}`;
	// }
	const response = await fetch(host + url, {
		method: 'GET',
		headers: headers
	});
	const data = await response.json();
	return data;
};

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
