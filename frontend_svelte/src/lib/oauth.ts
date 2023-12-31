import { PublicClientApplication } from '@azure/msal-browser';
import { writable } from 'svelte/store';




export const signIn = async (app_reg_client_id: string, azure_authority: string, host: string) => {
  const msalConfig = {
    auth: {
      clientId: app_reg_client_id,
      authority: azure_authority,
      redirectUri: `${host}/oauth/callback`,
    },
  };
  console.log(msalConfig);

  const initialMsalInstance = await new PublicClientApplication(msalConfig);
  await initialMsalInstance.initialize();

  const msalInstanceStore = writable(initialMsalInstance)

  // const redirectUri = `${host}/oauth/callback`;
  try {
    const redirectUri = `${host}/oauth/callback`;
    const response = await initialMsalInstance.loginRedirect({ 
      // scopes: ["read.all"],// TBD: fix scopes to the ones registered in app registration
      // scopes: [`api://${configuration.api_scope}`],
      scopes: [],
      // redirectUri: redirectUri
    }); // add scopes here?
    console.log(response);
    return response;
  } catch (err) {
    console.error(err);
  }
};
