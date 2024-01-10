import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ( ) => {
	console.log("IMPLMENT logout!");
};

// import type { PageServerLoad } from './$types';

// // export const load: PageServerLoad = async ({ cookies }) => {
// export const load: PageServerLoad = async ({  }) => {
// 	// cookies.delete('accessToken');
// };
