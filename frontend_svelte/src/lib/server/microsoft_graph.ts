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
  return data
}

export const getMicrosoftGraphBlob = async ( account: AccountInfo, endpoint: string ): Promise<Response> => {
  const accessToken = await getAccessToken( account);
  const response = await fetch(`${ms_graph_api_base_uri}/${endpoint}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });
  console.log("=> microsoft_graphBlob - getMicrosoftGraph - response headers - Content-Type");
  console.log( response.headers.get('Content-Type') );
  console.log("=> microsoft_graphBlob - getMicrosoftGraph - response headers - Content-Length");
  console.log( response.headers.get('Content-Length') );
  console.log("=> microsoft_graphBlob - getMicrosoftGraph - response headers - transfer-encoding");
  console.log( response.headers.get('transfer-encoding') );
  return response
}
