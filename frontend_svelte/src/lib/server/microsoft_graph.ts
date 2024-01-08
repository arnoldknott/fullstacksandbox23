import type { AccountInfo } from "@azure/msal-node";
import { getAccessToken } from "./oauth";

const ms_graph_api_base_uri = 'https://graph.microsoft.com/v1.0';

export const getMicrosoftGraphData = async ( account: AccountInfo, endpoint: string ): Promise<string> => {
  const accessToken = await getAccessToken( account);
  const response = await fetch(`${ms_graph_api_base_uri}/${endpoint}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });
  const data = await response.json();
  // console.log("microsoft_graph - getMicrosoftGraph - data");
  // console.log( data );
  return data
}

export const getMicrosoftGraphBlob = async ( account: AccountInfo, endpoint: string ): Promise<Response> => {
  const accessToken = await getAccessToken( account);
  const response = await fetch(`${ms_graph_api_base_uri}/${endpoint}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });
  // console.log("microsoft_graph - getMicrosoftGraph - response");
  // console.log(response )
  // console.log( response.body)
  // return response
  // const file = await response.blob();
  // console.log("microsoft_graph - getMicrosoftGraph - blob");
  // console.log( file );
  // console.log("=> microsoft_graphBlob - getMicrosoftGraph - response");
  // console.log(response);
  console.log("=> microsoft_graphBlob - getMicrosoftGraph - response headers - Content-Type");
  console.log( response.headers.get('Content-Type') );
  console.log("=> microsoft_graphBlob - getMicrosoftGraph - response headers - Content-Length");
  console.log( response.headers.get('Content-Length') );
  console.log("=> microsoft_graphBlob - getMicrosoftGraph - response headers - transfer-encoding");
  console.log( response.headers.get('transfer-encoding') );
  return response
}


// TBD: delete all of this - relicts from client side authentication:

// import type { Authentication } from './oauth';
// import { auth_instance_store } from './stores';
// import { get } from 'svelte/store';

// import { getAccessToken } from "./oauth";

// import MicrosoftOauth from '$lib/server/oauth';

// const ms_graph_api_base_uri = 'https://graph.microsoft.com/v1.0';

// export const get_user_picture = async () => {
//   // const auth = get(auth_instance_store);
//   // const scopes = ["User.Read"]
//   // const access_token = await auth?.getAccessToken(scopes);
//   // console.log("get_user_picture - access_token");
//   // console.log(access_token);
//   // const access_token = await getAccessToken(["User.Read"]);
//   const access_token = null
//   const response = await fetch(`${ms_graph_api_base_uri}/me/photo/$value`, {
//     headers: {
//       Authorization: `Bearer ${access_token}`
//     }
//   });
//   // console.log("microsoft_graph - get_user_picture - response");
//   // console.log(response);
//   return response;
// }
//
// export const get_ms_graph = async ( endpoint: string ) => {
//   console.log("Hello from lib/server/get_ms_graph - endpoint");
//   console.log(endpoint);
//   // const auth = get(auth_instance_store);
//   // const scopes = ["User.Read"]
//   // const access_token = await auth?.getAccessToken(scopes);
//   // console.log("get_user_picture - access_token");
//   // console.log(access_token);
//   // const access_token = await getAccessToken(["User.Read"]);

//   // Seems to (still) work without access token:
//   // const client = MicrosoftOauth.getInstance()
//   // const tokenCache = await client.getTokensFromCache()
//   // console.log("get_ms_graph - tokensFromCache");
//   // console.log(tokenCache);

//   // const accounts = await tokenCache.getAllAccounts()
//   // console.log("get_me - accounts");
//   // console.log(accounts);
//   // const response = await fetch(`${ms_graph_api_base_uri}/me/`, {
//   //   headers: {
//   //     Authorization: `Bearer ${access_token}`
//   //   }
//   // });
//   // console.log("microsoft_graph - get_user_picture - response");
//   // console.log(response);
//   // return response;
// }