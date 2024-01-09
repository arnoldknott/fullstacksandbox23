// import type { AccountInfo } from "@azure/msal-node";
// import { getAccessToken } from "./oauth";
// import type { Session } from "$lib/types"

// const ms_graph_api_base_uri = 'https://graph.microsoft.com/v1.0';

console.log("Hello from totally irrelevant microsoft_graph.ts");

// Another rebuild of the fetch function available in server load functions
// Just make a worker function, that helps getting accessToken from sessionData
// export const getMicrosoftGraphData = async ( session: Session, endpoint: string ): Promise<string> => {
//   const accessToken = await getAccessToken( session );
//   const response = await fetch(`${ms_graph_api_base_uri}/${endpoint}`, {
//     headers: {
//       Authorization: `Bearer ${accessToken}`
//     }
//   });
//   const data = await response.json();
//   return data
// }

// export const getMicrosoftGraphBlob = async ( session: Session, endpoint: string ): Promise<Response> => {
//   const accessToken = await getAccessToken( session);
//   const response = await fetch(`${ms_graph_api_base_uri}/${endpoint}`, {
//     headers: {
//       Authorization: `Bearer ${accessToken}`
//     }
//   });
//   return response
// }
