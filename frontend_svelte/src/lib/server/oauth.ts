// import { app_config } from './config';
import AppConfig from './config';
import { ConfidentialClientApplication, type AuthenticationResult } from '@azure/msal-node';
import type { Session } from '$lib/types';
import { building } from '$app/environment';

const appConfig = await AppConfig.getInstance();
// const scopesBackend = [appConfig.api_scope_default]
const scopesBackend = [ `api://${appConfig.api_scope}/api.read`, `api://${appConfig.api_scope}/api.write` ]
const scopesMsGraph = [ "User.Read", "openid", "profile", "offline_access" ]

let msalConfClient: ConfidentialClientApplication | null = null;

// construct a user consent urL: https://login.microsoftonline.com/{tenant-id}/authorize?client_id={client-id}
// https://login.microsoftonline.com/<tenant-id-here>/v2.0/authorize?client_id=<client-id-here>&scope=<scope-here>&redirect_uri=http%3A%2F%2Flocalhost%2Foauth%2Fcallback
const createMsalConfClient = async () => {
  if (!msalConfClient){
    // const configuration = await app_config();
    // const appConfig = await AppConfig.getInstance();
    // console.log(appConfig.keyvault_health)

    const msalConfig = {
      auth: {
        clientId: appConfig.app_reg_client_id,
        authority: appConfig.az_authority, 
        clientSecret: appConfig.app_client_secret,
        scopes: [ ...scopesBackend, ...scopesMsGraph ],
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
    console.log("👍 🔥oauth - Authentication - MsalConfClient - created!");
    // TBD: remove cache clearing: debugging ony
    // msalConfClient.clearCache()
    // console.log("💻 🔥oauth - Authentication - MsalConfClient - cacheCleared!");
  }
  return msalConfClient;
}

if (!building){
  try{
    await createMsalConfClient()
  } catch (err) {
    console.error("🔥 oauth - getTokens - msalConfClient could not created");
    throw err;
  }
}

const checkMsalConfClient = async () => {
  if (!msalConfClient){
    try{
      await createMsalConfClient()
    } catch (err) {
      console.error("🔥 oauth - getTokens - msalConfClient could not created");
      throw err;
    }
  }
  if (!msalConfClient){
    throw new Error("🔥 oauth - getTokens failed - msalConfClient not initialized");
  }
  return msalConfClient
}

export const signIn = async ( origin: string, scopes: string[] = [ ...scopesBackend, ...scopesMsGraph ] ): Promise<string> => {
  // Check if msalClient exists on very first login, if not create it.
  // const appConfig = AppConfig.getInstance();
  // console.log("oauth - Authentication - signIn - appConfig: ");
  // console.log(appConfig.keyvault_health);
  msalConfClient ? null : await createMsalConfClient()
  const authCodeUrlParameters = {
    scopes: scopes,
    redirectUri: `${origin}/oauth/callback`
  };
  let authCodeUrl: string
  try {
    const msalConfClient = await  checkMsalConfClient()
    authCodeUrl = await msalConfClient.getAuthCodeUrl(authCodeUrlParameters);
  } catch (err) {
    console.error("🔥 oauth - Authentication - signIn failed");
    console.error(err);
    throw err;
  }
  return authCodeUrl;
}

export const authenticateWithCode = async(code: string | null, origin: string, scopes: string[] = scopesMsGraph ): Promise<AuthenticationResult> =>  {
  if (!code) {
    throw new Error("🔥 oauth - GetAccessToken failed - no code");
  }
  try {
    const msalConfClient = await checkMsalConfClient()
    const response = await msalConfClient.acquireTokenByCode({
      code: code,
      scopes: scopes,
      redirectUri: `${origin}/oauth/callback`,
    });
    // const tokenCache = msalConfClient.getTokenCache();
    // const accounts = await tokenCache.getAllAccounts();
    return response;
  } catch (err) {
    console.error("🔥 oauth - GetAccessToken failed");
    console.error(err);
    throw err
  }
}

export const getAccessToken = async ( sessionData: Session, scopes: string[] = [appConfig.api_scope_default] ): Promise<string> => {
  const msalConfClient = await  checkMsalConfClient()
  const account = sessionData.account;
  try {
    const response = await msalConfClient.acquireTokenSilent({
    scopes: scopes,
    account: account,
    });
    const accessToken = response.accessToken;
    return accessToken
  } catch (err) {
    console.error("🔥 oauth - GetAccessToken failed");
    console.error(err);
    throw err
  }  
}

// export const getAccessTokenMsGraph = async ( sessionData: Session ): Promise<string> => {
//   const accessToken = await getAccessToken(sessionData, ["User.Read"])
//   return accessToken
// }

// export const signOut = async ( ): Promise<void> => {
//   // TBD: implement logout
//   // try {
//   //   const msalConfClient = await  checkMsalConfClient()
//   //   // implement logout
//   // } catch (err) {
//   //   console.error("🔥 oauth - Logout failed: ", err);
//   //   throw err
//   // }
// }


console.log("👍 🔥 lib - server - oauth.ts - end");