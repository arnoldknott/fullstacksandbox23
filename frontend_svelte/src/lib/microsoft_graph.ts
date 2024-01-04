// import type { Authentication } from './oauth';
// import { auth_instance_store } from './stores';
// import { get } from 'svelte/store';

import { getAccessToken } from "./oauth";

const ms_graph_api_base_uri = 'https://graph.microsoft.com/v1.0';


export const get_user_picture = async () => {
  // const auth = get(auth_instance_store);
  // const scopes = ["User.Read"]
  // const access_token = await auth?.getAccessToken(scopes);
  // console.log("get_user_picture - access_token");
  // console.log(access_token);
  const access_token = await getAccessToken(["User.Read"]);
  const response = await fetch(`${ms_graph_api_base_uri}/me/photo/$value`, {
    headers: {
      Authorization: `Bearer ${access_token}`
    }
  });
  // console.log("microsoft_graph - get_user_picture - response");
  // console.log(response);
  return response;
}