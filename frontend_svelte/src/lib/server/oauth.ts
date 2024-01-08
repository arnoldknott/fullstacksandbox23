import { app_config } from './config';
import { ConfidentialClientApplication, type AuthenticationResult, type TokenCache, type AccountInfo } from '@azure/msal-node';

const configuration = await app_config();
const scopes = ["User.Read"];

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

const msalConfClient = new ConfidentialClientApplication(msalConfig);

export const signIn = async ( origin: string): Promise<string> => {
  const authCodeUrlParameters = {
    scopes: ["User.Read"],
    redirectUri: `${origin}/oauth/callback`
  };
  let authCodeUrl: string
  try {
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

export const getAccessToken = async ( account: AccountInfo): Promise<string> => {
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
  } catch (err) {
    console.error("oauth - Logout failed: ", err);
    throw err
  }

}
