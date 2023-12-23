// import { postBackend, getBackend } from '$lib/backend';
// import { user_store } from '$lib/stores';
// import { error } from '@sveltejs/kit';

// // TBD: add type PageServerLoad here?
// export const actions = {
// 	default: async ({ cookies, request }) => {
// 		const data = await request.formData();
// 		const payloadLogin = {
// 			email: data.get('email')?.toString() || '',
// 			password: data.get('password')?.toString() || ''
// 		};
// 		const accessToken = await postBackend('/api/user/token/', payloadLogin);
// 		let response = {
// 			status: NaN,
// 			body: {},
// 			redirect: ''
// 		};
// 		if (
// 			!accessToken ||
// 			accessToken.token === 'undefined' ||
// 			accessToken.detail === 'Invalid token.'
// 		) {
// 			response = {
// 				status: 401,
// 				body: {
// 					message: 'Unauthorized'
// 				},
// 				redirect: '/login'
// 			};
// 		} else {
// 			const user = await getBackend('/api/user/me/', accessToken.token);
// 			user.loggedIn = true;
// 			user_store.set(user);
// 			cookies.set('accessToken', accessToken.token);
// 			response = {
// 				status: 200,
// 				body: {
// 					message: 'userLoggedIn'
// 				},
// 				redirect: '/dashboard'
// 			};
// 		}
// 		return response;
// 	}
// };
