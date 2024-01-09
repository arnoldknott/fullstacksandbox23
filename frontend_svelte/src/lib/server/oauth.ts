import { app_config } from './config';
import { ConfidentialClientApplication, type AuthenticationResult } from '@azure/msal-node';
import type { Session } from '$lib/types';

const scopes = ["User.Read"];

let msalConfClient: ConfidentialClientApplication | null = null;

const createMsalConfClient = async () => {
  if (!msalConfClient){
    const configuration = await app_config();

    const msalConfig = {
      auth: {
        clientId: configuration.app_reg_client_id,
        authority: configuration.azure_authority, 
        clientSecret: configuration.app_client_secret,
        scopes: scopes
        /***********************************************************************************************************************************
        Configure persisting the cache to Redis - as soon as Redis is encrypted!
        https://github.com/AzureAD/microsoft-authentication-library-for-js/blob/dev/lib/msal-node/docs/caching.md#persistent-cache
        implementation of on-behalf-of-with-distributed-cache:
        https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/samples/msal-node-samples/on-behalf-of-distributed-cache
        implementation of on-behalf-of:
        https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/samples/msal-node-samples/on-behalf-of
        But not strictly necessary: right now the cache is in a protected network.
        ***********************************************************************************************************************************/
      },
    }
  
    msalConfClient = new ConfidentialClientApplication(msalConfig);
  }
  return msalConfClient;
}

export const signIn = async ( origin: string): Promise<string> => {
  // Check if msalClient exists on very first login, if not create it.
  msalConfClient ? null : await createMsalConfClient()
  const authCodeUrlParameters = {
    scopes: ["User.Read"],
    redirectUri: `${origin}/oauth/callback`
  };
  let authCodeUrl: string
  try {
    if (!msalConfClient){
      throw new Error("oauth - Authentication - signIn failed - msalConfClient not initialized");
    }
    authCodeUrl = await msalConfClient.getAuthCodeUrl(authCodeUrlParameters);
  } catch (err) {
    console.error("oauth - Authentication - signIn failed");
    console.error(err);
    throw err;
  }
  return authCodeUrl;
}

export const getTokens = async(code: string | null, origin: string): Promise<AuthenticationResult> =>  {
  if (!code) {
    throw new Error("oauth - GetAccessToken failed - no code");
  }
  try {
    if (!msalConfClient){
      throw new Error("oauth - Authentication - signIn failed - msalConfClient not initialized");
    }
    const response = await msalConfClient.acquireTokenByCode({
      code: code,
      scopes: scopes,
      redirectUri: `${origin}/oauth/callback`,
    });
    // const tokenCache = msalConfClient.getTokenCache();
    // const accounts = await tokenCache.getAllAccounts();
    return response;
  } catch (err) {
    console.error("oauth - GetAccessToken failed");
    console.error(err);
    throw err
  }
}

export const getAccessToken = async ( sessionData: Session ): Promise<string> => {
  if (!msalConfClient){
    throw new Error("oauth - Authentication - signIn failed - msalConfClient not initialized");
  }
  const account = sessionData.account;
  const response = await msalConfClient.acquireTokenSilent({
    scopes: scopes,
    account: account,
  });
  const accessToken = response.accessToken;
  return accessToken
}

export const signOut = async ( ): Promise<void> => {
  // TBD: implement logout
  try {
    if (!msalConfClient){
      throw new Error("oauth - Authentication - signIn failed - msalConfClient not initialized");
    }
    // implement logout
  } catch (err) {
    console.error("oauth - Logout failed: ", err);
    throw err
  }

}
