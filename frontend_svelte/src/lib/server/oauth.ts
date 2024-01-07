import { app_config } from './config';
import { ConfidentialClientApplication, type AuthenticationResult } from '@azure/msal-node';

class MicrosoftOauth {
  msalConfClient!: ConfidentialClientApplication

  private constructor( ) { }

  private async init() {
    const configuration = await app_config();

    const msalConfig = {
      auth: {
        clientId: configuration.app_reg_client_id,
        authority: configuration.azure_authority, 
        clientSecret: configuration.app_client_secret,
      },
    }
    this.msalConfClient = new ConfidentialClientApplication(msalConfig);
    // console.log('oauth - init - msalConfClient initialized with');
    // console.log('oauth - init - msalConfClient - clientId');
    // console.log(msalConfig.auth.clientId);
    // console.log('oauth - init - msalConfClient - authority');
    // console.log(msalConfig.auth.authority);
  }

  static async create() {
    const oauth = new MicrosoftOauth();
    await oauth.init();
    return oauth;
  }

  async signIn( origin: string): Promise<string> {
    // if (!MicrosoftOauth.msalConfClient) {
    //   MicrosoftOauth.msalConfClient = MicrosoftOauth.getInstance();
    // }
    const authCodeUrlParameters = {
      scopes: ["User.Read"],
      redirectUri: `${origin}/oauth/callback`
    };
    let authCodeUrl: string
    try {
      // const authCodeUrl = await MicrosoftOauth.msalConfClient.getAuthCodeUrl(authCodeUrlParameters);
      // console.log("oauth - Authentication - signIn - msalConfClient");
      authCodeUrl = await this.msalConfClient.getAuthCodeUrl(authCodeUrlParameters);
    } catch (err) {
      console.error("oauth - Authentication - signIn failed");
      console.error(err);
      throw err;
    }
    // console.log("oauth - Authentication - signIn - authCodeUrl");
    // console.log(authCodeUrl);
    return authCodeUrl;
  }

  async getTokens(code: string | null, scopes: string[] = [], origin: string): Promise<AuthenticationResult> {
    if (!this.msalConfClient) {
      throw new Error("oauth - GetAccessToken failed - no msalConfClient");
    }
    if (!code) {
      throw new Error("oauth - GetAccessToken failed - no code");
    }
    try {
      const response = await this.msalConfClient.acquireTokenByCode({
        code: code,
        scopes: scopes,
        redirectUri: `${origin}/oauth/callback`,
      });
      // console.log("oauth - Authentication - GetAccessToken - response");
      // console.log(response);
      return response;
    } catch (err) {
      console.error("oauth - GetAccessToken failed");
      console.error(err);
      throw err
    }
  }
  async getTokensFromCache(scopes: string[] = []): Promise<AuthenticationResult> {
    if (!this.msalConfClient) {
      throw new Error("oauth - GetTokenCache failed - no msalConfClient");
    }
    try {

      const tokenCache = this.msalConfClient.getTokenCache();
      // console.log("oauth - Authentication - GetTokenCache - tokenCache");
      // console.log(tokenCache);
      const accounts = await tokenCache.getAllAccounts();
      // console.log("oauth - Authentication - GetTokenCache - accounts");
      // console.log(accounts);
      const response = await this.msalConfClient.acquireTokenSilent({
        // scopes: ["User.Read"],
        scopes: scopes,
        // TBD: accounts are not available here! Get from Cache!!
        account: accounts[0],
      });
      // console.log("oauth - Authentication - TokenCache - response");
      // console.log(response);
      return response;
    } catch (err) {
      console.error("oauth - GetAccessToken failed");
      console.error(err);
      throw err
    }
  }

  async signOut( ): Promise<void> {
    try {
      await this.msalConfClient.clearCache();
    } catch (err) {
      console.error("oauth - Logout failed: ", err);
      throw err// error(404, 'Logout failed')
    }
  
  }
  
}

export default MicrosoftOauth;

// Not good: this is singleton gets stored on the server without being attached to the user
// Bob might be able to get to Alice's version of Singleton, and therefore could access the 
// export class MicrosoftOauth {
//   private static msalConfClient: ConfidentialClientApplication

//   private constructor( ) {}

//   public static getInstance(): MicrosoftOauth {
//     if (!MicrosoftOauth.msalConfClient) {
//       MicrosoftOauth.msalConfClient = new ConfidentialClientApplication(msalConfig);
//     }
//     return new MicrosoftOauth();
//   }

  // async signIn( origin: string): Promise<string> {
  //   // if (!MicrosoftOauth.msalConfClient) {
  //   //   MicrosoftOauth.msalConfClient = MicrosoftOauth.getInstance();
  //   // }
  //   const authCodeUrlParameters = {
  //     scopes: ["User.Read"],
  //     redirectUri: `${origin}/oauth/callback`
  //   };
  //   let authCodeUrl: string
  //   try {
  //     // const authCodeUrl = await MicrosoftOauth.msalConfClient.getAuthCodeUrl(authCodeUrlParameters);
  //     authCodeUrl = await MicrosoftOauth.msalConfClient.getAuthCodeUrl(authCodeUrlParameters);
  //   } catch (err) {
  //     console.error("oauth - Authentication - signIn failed");
  //     console.error(err);
  //     throw err;
  //   }
  //   // console.log("oauth - Authentication - signIn - authCodeUrl");
  //   // console.log(authCodeUrl);
  //   return authCodeUrl;
  // }

  // async getTokens(code: string | null, scopes: string[] = [], origin: string): Promise<AuthenticationResult> {
  //   if (!MicrosoftOauth.msalConfClient) {
  //     throw new Error("oauth - GetAccessToken failed - no msalConfClient");
  //   }
  //   if (!code) {
  //     throw new Error("oauth - GetAccessToken failed - no code");
  //   }
  //   try {
  //     const response = await MicrosoftOauth.msalConfClient.acquireTokenByCode({
  //       code: code,
  //       scopes: scopes,
  //       redirectUri: `${origin}/oauth/callback`,
  //     });
  //     // console.log("oauth - Authentication - GetAccessToken - response");
  //     // console.log(response);
  //     return response;
  //   } catch (err) {
  //     console.error("oauth - GetAccessToken failed");
  //     console.error(err);
  //     throw err
  //   }
  // }

//   async getTokensFromCache(scopes: string[] = []): Promise<AuthenticationResult> {
//     if (!MicrosoftOauth.msalConfClient) {
//       throw new Error("oauth - GetTokenCache failed - no msalConfClient");
//     }
//     try {

//       const tokenCache = MicrosoftOauth.msalConfClient.getTokenCache();
//       // console.log("oauth - Authentication - GetTokenCache - tokenCache");
//       // console.log(tokenCache);
//       const accounts = await tokenCache.getAllAccounts();
//       // console.log("oauth - Authentication - GetTokenCache - accounts");
//       // console.log(accounts);
//       const response = await MicrosoftOauth.msalConfClient.acquireTokenSilent({
//         // scopes: ["User.Read"],
//         scopes: scopes,
//         // TBD: accounts are not available here! Get from Cache!!
//         account: accounts[0],
//       });
//       // console.log("oauth - Authentication - TokenCache - response");
//       // console.log(response);
//       return response;
//     } catch (err) {
//       console.error("oauth - GetAccessToken failed");
//       console.error(err);
//       throw err
//     }
//   }

//   async signOut( ): Promise<void> {
//     try {
//       await MicrosoftOauth.msalConfClient.clearCache();
//     } catch (err) {
//       console.error("oauth - Logout failed: ", err);
//       throw err// error(404, 'Logout failed')
//     }
  
//   }
  
// }

// export default MicrosoftOauth;


// SECOND VERSION - CLIENT SIDE OAUTH - WITH CLASS


// import { PublicClientApplication, type AccountInfo, InteractionRequiredAuthError, type AuthenticationResult } from '@azure/msal-browser';



// export class Authentication {
//   msalInstance: PublicClientApplication


//   constructor(clientId: string, authority: string) {
//     const msalConfig = {
//       auth: {
//         clientId: clientId,
//         authority: authority, 
//       },
//     }
//     this.msalInstance = new PublicClientApplication(msalConfig);
//   }
  
//   async initialize(): Promise<PublicClientApplication> {
//     await this.msalInstance.initialize();
//     await this.msalInstance.handleRedirectPromise();
//     // console.log("oauth - msalInstance initialized");
//     return this.msalInstance;
//   }
    
//   // TBD: add scopes!
//   async signIn(redirectOrigin: string): Promise<AuthenticationResult | null> {
//     try {
//       await this.msalInstance.handleRedirectPromise();
//       this.msalInstance.loginRedirect({
//       // scopes: ["read.all"],// TBD: fix scopes to the ones registered in app registration
//       // scopes: [`api://${configuration.api_scope}`],
//       scopes: [],
//       redirectUri: `${redirectOrigin}/oauth/callback`
//     });
//     const response = await this.msalInstance.handleRedirectPromise();
//     return response;
//   } catch (err) {
//     // if ( error instanceof BrowserAuthError) {
//     //   // console.log('Interaction in progress, retrieving active account');
//     //   await initialMsalInstance.getActiveAccount().setInteractionInProgress(false);
//     // } else {
//     console.error("oauth - Login failed: ", err);
//     throw err
//     // }
//   }
// }

// async getAccount(): Promise<AccountInfo> {
//   try {
//     await this.msalInstance.handleRedirectPromise();
//     const accounts = this.msalInstance.getAllAccounts();
//     // console.log("oauth - GetAccount - accounts");
//     // console.log(accounts);
//     return accounts[0];
//   } catch (err) {
//     console.error("oauth - GetAccount failed: ", err);
//     throw err
//   }

// }

// async getAccessToken( scopes: string[] = []): Promise<string | undefined> {
//   try {
//     await this.msalInstance.handleRedirectPromise();
//     const account = await this.getAccount();
//     const tokenRequest = {
//       scopes: scopes,
//       account: account,
//     }
//     try{
//       const response = await this.msalInstance.acquireTokenSilent(tokenRequest);
//       // console.log("oauth - Authentication - GetAccessToken - response.accessToken");
//       // console.log(response.accessToken);
//       return response.accessToken;
//       } catch (error) {
//         if( error instanceof InteractionRequiredAuthError) {
//           // EventMessageUtils.getInteractionStatusFromEvent(TBD: find correct EventMessage here)
//           // await this.msalInstance.getInteractionStatusFromEvent() 
//           // if (myGlobalState.getInteractionStatus() !== InteractionStatus.None) {
//           //   // throw a new error to be handled in the caller below
//           //   throw new Error("interaction_in_progress");
//           const tokenRequestNew = {
//             ...tokenRequest,
//             redirectUri: `${window.location.origin}/oauth/callback`,
//           }
//           await this.msalInstance.acquireTokenRedirect(tokenRequestNew)
//         } else {
//           console.error("oauth - GetAccessToken failed - no AuthError: ", error);
//           throw error;
//         }
//       }
//   } catch (err) {
//     console.error("oauth - GetAccessToken failed: ", err);
//     throw err
//   }

// }

// async signOut(redirectOrigin: string, redirectUri: string = "/"): Promise<void> {
//   try {
//     await this.msalInstance.handleRedirectPromise();
//     // console.log("oauth - signout - redirectUri");
//     // console.log(`${redirectOrigin}${redirectUri}`);
//     // const accounts = this.msalInstance.getAllAccounts();
//     // TBD: add account to logoutRedirect
//     await this.msalInstance.logoutRedirect({
//       postLogoutRedirectUri: `${redirectOrigin}${redirectUri}`
//     });
//   } catch (err) {
//     console.error("oauth - Logout failed: ", err);
//     throw err// error(404, 'Logout failed')
//   }
//   }
// }

// export const getAccessToken = async (scopes: string[] = []): Promise<string | undefined> => {
//   const auth = get(auth_instance_store);
//   const accessToken = await auth?.getAccessToken(scopes);
//   // console.log("oauth - getAccessToken - response.accessToken");
//   // console.log(accessToken);
//   return accessToken;
// }

// export default Authentication;



// FIRST VERSION - CLIENT SIDE OAUTH - WITHOUT CLASS


// export const createAuthentication = () =>  {
//   const authInstance = new Authentication(configuration.app_reg_client_id, configuration.azure_authority)
//   console.log('auth created a new authInstance')
//   auth_instance_store.set(authInstance);
// }


// const msalConfig = {
//   auth: {
//     clientId: configuration.app_reg_client_id,
//     authority: configuration.azure_authority, 
//   },
// }

// export const signIn = async (app_reg_client_id: string, azure_authority: string, host: string) => {
//   const msalConfig = {
//     auth: {
//       clientId: app_reg_client_id,
//       authority: azure_authority,
//       redirectUri: `${host}/oauth/callback`,
//     },
//     // cacheOptions: {
//     //   storeAuthStateInCookie: true,
//     //   secureCookies: true
//     // }
//   };
//   // console.log("oauth - signin - msalConfig");
//   // console.log(msalConfig);

//   const initialMsalInstance = await new PublicClientApplication(msalConfig);
//   await initialMsalInstance.initialize();

//   // sessionStorage.setItem("msal.initialMsalInstance", JSON.stringify(initialMsalInstance));
//   // console.log("oauth - signin - initialMsalInstance");
//   // console.log(initialMsalInstance);

//   //TBD: put msalInstance in Svelte store and use the one from the store in the rest of the application!
//   // const msalInstanceStore = writable(initialMsalInstance)
//   // msalInstanceStore.set(initialMsalInstance);
//   // let msalInstance = get( msalInstanceStore );
//   // const msalInstance = get( msalInstanceStore );

//   // const redirectUri = `${host}/oauth/callback`;
//   try {
//     // const redirectUri = `${host}/oauth/callback`;
//     initialMsalInstance.loginRedirect({ 
//       // scopes: ["read.all"],// TBD: fix scopes to the ones registered in app registration
//       // scopes: [`api://${configuration.api_scope}`],
//       scopes: [],
//       // redirectUri: redirectUri
//     }); // add scopes here?
//     const response = await initialMsalInstance.handleRedirectPromise();
//     sessionStorage.setItem("msal.responseLoginRedirect", JSON.stringify(response));
//     console.log("oauth - signin - response");
//     console.log(response);
//     console.log("oauth - signin - response?.idToken");
//     console.log(response?.idToken);
//     return response;
//   } catch (err) {
//     // if ( error instanceof BrowserAuthError) {
//     //   // console.log('Interaction in progress, retrieving active account');
//     //   await initialMsalInstance.getActiveAccount().setInteractionInProgress(false);
//     // } else {
//     // console.error(err);
//     throw err
//     // }
//   }
// };

// // not perfectly working yet - uses another msalinstance to logout!
// export const signOut = async (app_reg_client_id: string, azure_authority: string, host: string) => {
//   console.log("oauth - signout");
//   const msalConfig = {
//     auth: {
//       clientId: app_reg_client_id,
//       authority: azure_authority,
//       redirectUri: `${host}/oauth/callback`,
//     },
//   }
//   const msalInstance = new PublicClientApplication(msalConfig);
//   await msalInstance.initialize();
//   console.log("oauth - signout - msalInstance");
//   console.log(msalInstance);
//   msalInstance.logoutRedirect()
//   // const msalInstance = get( msalInstanceStore );
//   // console.log("oauth - signout - msalInstance");
//   // console.log(msalInstance);
//   // await msalInstance?.logoutRedirect();
//   // await msalInstance?.logoutRedirect({
//   //   postLogoutRedirectUri: `${window.location.origin}/`
//   // });
// }