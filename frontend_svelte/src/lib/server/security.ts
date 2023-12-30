// import { PublicClientApplication } from '@azure/msal-browser';
// import { app_config } from './config';


// const configuration = await app_config();


// const msalConfig = {
//   auth: {
//     clientId: configuration.app_reg_client_id,
//     authority: configuration.authority,
//   },
// };

// // export const msalInstance = new PublicClientApplication(msalConfig);

// export const loginRequest = async (host: string) => {

//   const redirectUri = `${host}/oauth/callback`;
//   try {
//     const redirectUri = `${host}/oauth/callback`;
//     const response = await msalInstance.loginPopup({ 
//       scopes: ["read.all"],// TBD: fix scopes to the ones registered in app registration
//       redirectUri: redirectUri
//     }); // add scopes here?
//     console.log(response);
//     return response;
//   } catch (err) {
//     console.error(err);
//   }
// };

// export const loginRequest = async ( host: string ) => {
//   const msalConfig = {
//     auth: {
//     clientId: app_config().app_reg_client_id,
//     authority: app_config().authority,
//     redirectUri: host,
//     },
//   }

//   const msalInstance = new PublicClientApplication(msalConfig);

//   try {
//     const response = await msalInstance.loginPopup();// add scopes here?
//     console.log(response);
//     return response;
//   }
//   catch (err) {
//     console.error(err);
//   }