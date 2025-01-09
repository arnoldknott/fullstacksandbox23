import type { PageServerLoad } from "./$types";
import { backendAPI } from "$lib/server/apis";

export const load: PageServerLoad = async ({ locals }) => {
    const sessionId = locals.sessionData.sessionId;

    const responseMe = await backendAPI.get(sessionId, '/user/me');
    const me = await responseMe.json();
    // return {
    //     me: me
    // };
}