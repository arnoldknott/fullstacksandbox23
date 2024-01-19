import AppConfig from "$lib/server/config";
import type { Actions } from "./$types";
import type { PageServerLoad } from "./$types";

const appConfig = await AppConfig.getInstance();

export const actions = {
  default: async () => {
    await appConfig.updateValues()
  }
} satisfies Actions

export const load: PageServerLoad = async (  ) => {
  // TBD: we need the external url here - not the one inside the network
  return { body: `http://localhost:8660/docs` };
  // return { body: `${appConfig.backend_origin}/docs` };
}