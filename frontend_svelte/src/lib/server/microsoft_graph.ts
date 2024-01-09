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
  return response
}
