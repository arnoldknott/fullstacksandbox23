// import { postBackend } from '$lib/backend';
// import { user_store } from '$lib/stores';
// import { error } from '@sveltejs/kit';

// TBD: add type PageServerLoad here?
// export const actions = {
// 	default: async ({ cookies, request }) => {
// 		const data = await request.formData();
// 		const payloadRegister = {
// 			name: data.get('name')?.toString() || '',
// 			email: data.get('email')?.toString() || '',
// 			password: data.get('password')?.toString() || ''
// 		};
// 		const userCreated = await postBackend('/api/user/create/', payloadRegister);
// 		const user = userCreated;
// 		user.loggedIn = true;
// 		user_store.set(user);
// 		const payloadAuthenticate = {
// 			email: payloadRegister.email,
// 			password: payloadRegister.password
// 		};
// 		const accessToken = await postBackend('/api/user/token/', payloadAuthenticate);
// 		cookies.set('accessToken', accessToken.token);
// 		return {
// 			status: 200,
// 			body: {
// 				userCreated
// 			},
// 			redirect: '/dashboard'
// 		};
// 	}
// };
// 	if (schema === null) {
// 		return error(404, 'Unavailable');
// 	}
// 	return schema;
// };
