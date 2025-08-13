import type { PageServerLoad } from './$types';
import { backendAPI } from '$lib/server/apis/backendApi';
import type { UeberGroup } from '$lib/types';

export const load: PageServerLoad = async ({ locals, params }) => {
    const sessionId = locals.sessionData.sessionId;

    const response = await backendAPI.get(sessionId, `/uebergroup/${params.ueberGroupId}`);
    if (response.status === 200) {
        const thisUeberGroup: UeberGroup = await response.json();
        return {
            thisUeberGroup
        };
    } else {
        console.error('Error fetching Ueber Group:', response.status);
    }
};
