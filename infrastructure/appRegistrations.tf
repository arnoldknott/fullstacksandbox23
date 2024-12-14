# resource "random_uuid" "apiURI" {}
resource "random_uuid" "UuidScope1" {}
resource "random_uuid" "UuidScope2" {}
resource "random_uuid" "UuidScope3" {}
resource "random_uuid" "UuidScope4" {}
# resource "random_uuid" "UuidScope5" {}
# resource "random_uuid" "UuidScope6" {}
resource "random_uuid" "UuidRole1" {}     # Used for admins in backend
resource "random_uuid" "userGroupUUID" {} # Used for users in backend
# resource "random_uuid" "AIpublicRoleUUID" {}
# resource "random_uuid" "AIprivateRoleUUID" {}
# resource "random_uuid" "GitHubUserRoleUUID" {} # manage through account linking!
# resource "random_uuid" "DiscordUserRoleUUID" {} # manage through account linking!
# resource "random_uuid" "UuidRole5" {}

# # get the application ids for the well known applications to configure ms graph access:
# data "azuread_service_principal" "msgraph" {
#   client_id = data.azuread_application_published_app_ids.well_known.result["MicrosoftGraph"]
# }

resource "azuread_application" "backendAPI" {
  display_name = "${var.project_name}-backendAPI-${terraform.workspace}"
  # owners                  = [data.azuread_client_config.current.object_id, var.owner_object_id]
  owners                  = [var.owner_object_id, var.old_repo_service_principle_object_id, var.developer_localhost_object_id, var.managed_identity_github_actions_object_id]
  prevent_duplicate_names = true
  sign_in_audience        = "AzureADMyOrg"
  # Add the desired access groups manually in the portal
  # -> Entra AD -> Entreprise Applications
  # -> remove filter "Entreprise Applications"
  # -> find backend and add the relevant groups!
  # Get the group ID's and write them via API to the group database table
  # Add also to resources, where appropriate - maybe an admin frontend for that?
  group_membership_claims = ["ApplicationGroup"]

  lifecycle {
    ignore_changes = [identifier_uris]
  }

  api {
    // There's also a an "Authorized client applications" (preAuthorizedApplications in Manifest) section in portal, that also binds to the scopes. But deosn't appear in Terraform.
    // add manually: frontend as preAuthorizedApplication!
    known_client_applications      = [azuread_application.frontend.client_id]
    requested_access_token_version = 2

    # add this one later to prevent useres being asked for consent in the frontend
    # the application id is for the connected client applications
    # known_client_applications = [
    #   azuread_application.known1.application_id,
    # ]

    # oauth2_permission_scope {
    #   admin_consent_description  = "Allow the application to access a test user and session handling API for prototyping various applications on behalf of the signed-in user. See owner property for more information."
    #   admin_consent_display_name = "Access test user and session handling API"
    #   enabled                    = true
    #   id                         = random_uuid.UuidScope1.result
    #   type                       = "User"
    #   user_consent_description   = "Allow the application to access the test user and session handling API on your behalf."
    #   user_consent_display_name  = "Access test user and session handling API"
    #   value                      = "user_impersonation"
    # }

    oauth2_permission_scope {
      admin_consent_description  = "Gives the users of Fullstack Sandbox Application read rights to its REST API."
      admin_consent_display_name = "Users can read from Fullstack Sandbox REST API"
      enabled                    = true
      id                         = random_uuid.UuidScope2.result
      type                       = "User"
      user_consent_description   = "Enables you as user to read data from the Fullstack Sandbox."
      user_consent_display_name  = "Read data from Fullstack Sandbox"
      value                      = "api.read"
    }

    oauth2_permission_scope {
      admin_consent_description  = "Gives the users of Fullstack Sandbox Application write rights to its REST API."
      admin_consent_display_name = "Users can write to Fullstack Sandbox application's REST API"
      enabled                    = true
      id                         = random_uuid.UuidScope3.result
      type                       = "User"
      user_consent_description   = "Enables you as user to write data to the Fullstack Sandbox."
      user_consent_display_name  = "Write data to Fullstack Sandbox"
      value                      = "api.write"
    }

    oauth2_permission_scope {
      admin_consent_description  = "Gives the users of Fullstack Sandbox Application rights to interact with Fullstack application via socket.io."
      admin_consent_display_name = "Users can interact with Fullstack Sandbox via socket.io"
      enabled                    = true
      id                         = random_uuid.UuidScope4.result
      type                       = "User"
      user_consent_description   = "Enables you as user to use real-time communication, like chats in Fullstack Sandbox."
      user_consent_display_name  = "Real-time interaction with Fullstack Sandbox"
      value                      = "socketio"
    }

    # Handle through Roles: AIUser.public, AIUser.private, GitHubUser, DiscordUser, ...
    # oauth2_permission_scope {
    #   admin_consent_description  = "Gives the users of Fullstack Sandox Application rights to use public artifical intelligence within the app."
    #   admin_consent_display_name = "Users can use public artificial intelligence in Fullstack Sandbox"
    #   enabled                    = true
    #   id                         = random_uuid.UuidScope5.result
    #   type                       = "User"
    #   user_consent_description   = "Enables you as user to use the public artifical intelligence capabilities of Fullstack Sandbox."
    #   user_consent_display_name  = "Use public artificial intelligence in Fullstack Sandbox"
    #   value                      = "artificial_intelligence.public"
    # }

    # oauth2_permission_scope {
    #   admin_consent_description  = "Gives the users of Fullstack Sandox Application rights to use private artifical intelligence within the app."
    #   admin_consent_display_name = "Users can use private artificial intelligence in Fullstack Sandbox"
    #   enabled                    = true
    #   id                         = random_uuid.UuidScope6.result
    #   type                       = "User"
    #   user_consent_description   = "Enables you as user to use the private artifical intelligence capabilities of Fullstack Sandbox."
    #   user_consent_display_name  = "Use private artificial intelligence in Fullstack Sandbox"
    #   value                      = "artificial_intelligence.private"
    # }

    # add further scopes here:
    # add artificial.read, artificial.write, mapped_account.read, mapped_account.write, ...

  }

  # can be used to add groups to tokens and assign roles - but no correlation between role and group!
  # Defines roles within the app - mainly required for the backend,
  # but also used by the backendAPI to impersonate the user to access the Microsoft Graph API
  # and/or to access the backendAPI from postman/thunderclient:
  app_role {
    allowed_member_types = ["User"] # can also be ["User", "Application"], meaning 'User' or 'Application' on the Azure Tenant.
    description          = "Admins can manage the whole application"
    display_name         = "Admin"
    enabled              = true
    id                   = random_uuid.UuidRole1.result
    value                = "Admin"
  }

  app_role {
    allowed_member_types = ["User"] # can also be ["User", "Application"], meaning 'User' or 'Application' on the Azure Tenant.
    description          = "Users can access the content of the application"
    display_name         = "User" # Visible to end user
    enabled              = true
    id                   = random_uuid.userGroupUUID.result
    value                = "User" # could be comething like "User.Write" or "User.Read"
  }

  # User self-sign-up (after consent) - not possible without giving the
  # frontend app 'AppRoleAssignment.ReadWrite.All' and 'Application.Read.All'"
  # permissions, which appear overkill and need Admin consent.
  # app_role {
  #   allowed_member_types = ["User"]
  #   description          = "Users can access the public artificial intelligence"
  #   display_name         = "Public Artificial Intelligence Users"
  #   enabled              = true
  #   id                   = random_uuid.AIpublicRoleUUID.result
  #   value                = "publicAIuser"
  # }
  #
  # app_role {
  #   allowed_member_types = ["User"]
  #   description          = "Users can access the private artificial intelligence"
  #   display_name         = "Private Artificial Intelligence Users"
  #   enabled              = true
  #   id                   = random_uuid.AIprivateRoleUUID.result
  #   value                = "privateAIuser"
  # }

  # app_role {
  #   allowed_member_types = ["User"]
  #   description          = "Students can access their courses"
  #   display_name         = "Student"
  #   enabled              = true
  #   id                   = random_uuid.GitHubUserRoleUUID.result
  #   value                = "Student"
  # }

  # app_role {
  #   allowed_member_types = ["User"]
  #   description          = "Guest students can view courses"
  #   display_name         = "Guest Student"
  #   enabled              = true
  #   id                   = random_uuid.DiscordUserRoleUUID.result
  #   value                = "GuestStudent"
  # }

  # Grants the app access to the Microsoft Graph API with specific roles and scopes
  # required_resource_access {
  #   resource_app_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph

  #   resource_access {
  #     id   = "df021288-bdef-4463-88db-98f22de89214" # User.Read.All
  #     type = "Role"
  #   }

  #   # resource_access {
  #   #   id   = "b4e74841-8e56-480b-be8b-910348b18b4c" # User.ReadWrite
  #   #   type = "Scope"
  #   # }
  # }

  # MS Graph access to openid, profile and User.Read
  required_resource_access {
    resource_app_id = "00000003-0000-0000-c000-000000000000"

    ### Those are absolutely mandatory:
    # openid:
    resource_access {
      id   = "37f7f235-527c-4136-accd-4a02d197296e"
      type = "Scope"
    }

    # profile:
    resource_access {
      id   = "14dad69e-099b-42c9-810b-d002981feec1"
      type = "Scope"
    }

    # User.Read:
    resource_access {
      id   = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"
      type = "Scope"
    }

    # Additional:
    # Calendars.ReadWrite - delegated
    resource_access {
      id = "1ec239c2-d7c9-4623-a91a-a9775856bb36"
      type = "Scope"
    }

    # Calendars.ReadWrite.Shared - delegated
    resource_access {
      id   = "12466101-c9b8-439a-8589-dd09ee67e8e9"
      type = "Scope"
    }

    # Files.Read.All - delegated
    resource_access {
      id   = "df85f4d6-205c-4ac5-a5ea-6bf408dba283"
      type = "Scope"
    }

    # Files.ReadWrite.All - delegated
    resource_access {
      id   = "863451e7-0667-486c-a5d6-d135439485f0"
      type = "Scope"
    }

    # # Mail including the shared mailboxes - delegated:
    # # Mail.Read.Shared - delegated
    # resource_access {
    #   id   = "7b9103a5-4610-446b-9670-80643382c1fa"
    #   type = "Scope"
    # }

    # # Mail.ReadWrite.Shared - delegated
    # resource_access {
    #   id   = "5df07973-7d5d-46ed-9847-1271055cbd51"
    #   type = "Scope"
    # }

    # # Mail.Send.Shared - delegated
    # resource_access{
    #   id   = "a367ab51-6b49-43bf-a716-a1fb06d2a174"
    #   type = "Scope"
    # }

    # # Mail (only the users own) - delegated:
    # # Mail.Read - delegated
    # resource_access {
    #   id   = "570282fd-fa5c-430d-a7fd-fc8dc98a9dca"
    #   type = "Scope"
    # }

    # # Mail.ReadWrite - delegated
    # resource_access {
    #   id   = "024d486e-b451-40bb-833d-3e66d98c5c73"
    #   type = "Scope"
    # }

    # # Mail.Send - delegated
    # resource_access {
    #   id   = "e383f46e-2787-4529-855e-0e479a3ffac0"
    #   type = "Scope"
    # }

    # consider adding notes - for OneNote access

    # User.ReadBasic.All - delegated
    resource_access {
      id = "b340eb25-3456-403f-be2f-af7a0d370277"
      type = "Scope"
    }

    # Team.ReadBasic.All - delegated
    resource_access {
      id = "485be79e-c497-4b35-9400-0e3fa7f2a5d4"
      type = "Scope"
    }
  }


  # TBD: consider adding for enabling swaggerUI authentication - change the host names for stage and prod:
  # Example on how to connect SwaggerUI to AzureAD:
  # https://stackoverflow.com/questions/79259104/fastapi-azure-auth-proof-key-for-code-exchange-is-required-for-cross-origin-au/79260558#79260558
  single_page_application {
    redirect_uris = (terraform.workspace == "dev" ?
      [
        "http://localhost:8660/docs/oauth2-redirect",
        "https://${azurerm_container_app.BackendContainer.ingress[0].fqdn}/docs/oauth2-redirect",
      ] :
      [
        "https://${azurerm_container_app.BackendContainer.ingress[0].fqdn}/docs/oauth2-redirect",
      ]
    )
  }


  tags = [var.costcenter, var.owner_name, terraform.workspace]
}

# # creates a client secret for the frontend:
resource "azuread_application_password" "backendAPIClientSecret" {
  application_id = azuread_application.backendAPI.id
}

resource "azuread_application_identifier_uri" "backendAPIURI" {
  application_id = azuread_application.backendAPI.id
  identifier_uri = "api://${azuread_application.backendAPI.client_id}"
}

resource "azuread_service_principal" "servicePrinciple" { # TBD: consider renaming into "backendAPI"
  client_id                    = azuread_application.backendAPI.client_id
  app_role_assignment_required = false
  description                  = "Service principal for the fullStackSandbox23 application"
  # owners                       = [data.azuread_client_config.current.object_id, var.owner_object_id]
  owners = [var.owner_object_id, var.old_repo_service_principle_object_id, var.developer_localhost_object_id, var.managed_identity_github_actions_object_id]
}

resource "azuread_application_pre_authorized" "preAuthorizeFrontendatBackend" {
  application_id       = azuread_application.backendAPI.id
  authorized_client_id = azuread_application.frontend.client_id

  # TBD: add all scopes, that frontend needs to access backendAPI:
  permission_ids = [
    random_uuid.UuidScope2.result,
    random_uuid.UuidScope3.result,
    random_uuid.UuidScope4.result,
  ]
}

resource "azuread_application" "frontend" {
  display_name = "${var.project_name}-frontend-${terraform.workspace}"
  description  = "Frontend for the ${var.project_name} application"
  # owners                  = [data.azuread_client_config.current.object_id, var.owner_object_id]
  owners                  = [var.owner_object_id, var.old_repo_service_principle_object_id, var.developer_localhost_object_id, var.managed_identity_github_actions_object_id]
  prevent_duplicate_names = true
  sign_in_audience        = "AzureADMyOrg"
  group_membership_claims = ["ApplicationGroup"]


  # For OAuth2 Authorization Code Flow / on-behalf-of flow with ConfidentialClientApplication from @azure/msal-node
  web {
    redirect_uris = (terraform.workspace == "dev" ?
      [
        "http://localhost:8661/oauth/callback",
        "https://www.thunderclient.com/oauth/callback",
        "https://oauth.pstmn.io/v1/callback",
        "https://${azurerm_container_app.FrontendContainer.ingress[0].fqdn}/oauth/callback",
        # "https://${azurerm_container_app.FrontendContainer.ingress[0].fqdn}/oauth/tokens"
      ] :
      [
        # TBD: remove thunderclient before scalling app to bigger audience! -> requires a working administrative and admin frontend
        "https://www.thunderclient.com/oauth/callback",
        "https://oauth.pstmn.io/v1/callback",
        "https://${azurerm_container_app.FrontendContainer.ingress[0].fqdn}/oauth/callback",
        # "https://${azurerm_container_app.FrontendContainer.ingress[0].fqdn}/oauth/tokens"
      ]
    )
  }

  # To allow backendAPI to impersonate the user, that is logged in in the frontend, to access the Microsoft Graph API:
  # https://github.com/Azure-Samples/ms-identity-python-on-behalf-of
  required_resource_access {
    resource_app_id = "797f4846-ba00-4fd7-ba43-dac1f8f63013" # Azure Service Management API
    resource_access {
      id   = "41094075-9dad-400e-a0bd-54e686782033" # # Azure Service Management -> user_impersonation
      type = "Scope"
    }
  }


  privacy_statement_url = "https://www.dtu.dk/english/about/use-of-personal-data"

  # or
  # For Oauth2 Authorization Code Flow with PKCE from using PublicClientApplication from @azure/msal-browser
  # single_page_application {
  #   redirect_uris = ["http://localhost:8661/oauth/callback", "https://${azurerm_container_app.FrontendContainer.ingress[0].fqdn}:${azurerm_container_app.FrontendContainer.ingress[0].target_port}/oauth/callback"]
  # }

  tags = [var.costcenter, var.owner_name, terraform.workspace]
}

# # creates a client secret for the frontend:
resource "azuread_application_password" "frontendClientSecret" {
  application_id = azuread_application.frontend.id
}
