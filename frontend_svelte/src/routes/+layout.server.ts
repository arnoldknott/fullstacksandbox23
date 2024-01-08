import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import { getMicrosoftGraphData } from '$lib/server/microsoft_graph';

export const load: LayoutServerLoad = async ({ locals }) => {
  try {
    if (!locals.sessionData){
      console.error("layout - server - getMicrosoftGraph - userProfile - failed");
      redirect(307, "/");
    } else {
      const account = locals.sessionData.account;
      const userProfile = await getMicrosoftGraphData(account, '/me');
      return {
        userProfile: userProfile
      };
    }
  } catch {
    console.error("layout - server - getMicrosoftGraph - userProfile - failed");
  }
};