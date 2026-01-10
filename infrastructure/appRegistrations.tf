resource "random_uuid" "ScopeApiRead" {}
resource "random_uuid" "ScopeApiWrite" {}
resource "random_uuid" "ScopeSocketio" {}
resource "random_uuid" "RoleAdmin" {}       # Used for admins in backend
resource "random_uuid" "RoleUser" {}        # Used for users in backend
resource "random_uuid" "pgAdminRoleAdmin" { # Used for admins in pgAdmin
  count = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
}

# # get the application ids for the well known applications to configure ms graph access:
# data "azuread_service_principal" "msgraph" {
#   client_id = data.azuread_application_published_app_ids.well_known.result["MicrosoftGraph"]
# }

resource "azuread_application" "backendAPI" {
  display_name = "${var.project_name}-backendAPI-${terraform.workspace}"
  # owners                  = [data.azuread_client_config.current.object_id, var.owner_object_id]
  owners                  = [var.owner_object_id, var.developer_localhost_object_id, var.managed_identity_github_actions_object_id]
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
    known_client_applications      = [azuread_application.frontend.client_id, azuread_application.developerClients.client_id]
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
      id                         = random_uuid.ScopeApiRead.result
      type                       = "User"
      user_consent_description   = "Enables you as user to read data from the Fullstack Sandbox."
      user_consent_display_name  = "Read data from Fullstack Sandbox"
      value                      = "api.read"
    }

    oauth2_permission_scope {
      admin_consent_description  = "Gives the users of Fullstack Sandbox Application write rights to its REST API."
      admin_consent_display_name = "Users can write to Fullstack Sandbox application's REST API"
      enabled                    = true
      id                         = random_uuid.ScopeApiWrite.result
      type                       = "User"
      user_consent_description   = "Enables you as user to write data to the Fullstack Sandbox."
      user_consent_display_name  = "Write data to Fullstack Sandbox"
      value                      = "api.write"
    }

    oauth2_permission_scope {
      admin_consent_description  = "Gives the users of Fullstack Sandbox Application rights to interact with Fullstack application via socket.io."
      admin_consent_display_name = "Users can interact with Fullstack Sandbox via socket.io"
      enabled                    = true
      id                         = random_uuid.ScopeSocketio.result
      type                       = "User"
      user_consent_description   = "Enables you as user to use real-time communication, like chats in Fullstack Sandbox."
      user_consent_display_name  = "Real-time interaction with Fullstack Sandbox"
      value                      = "socketio"
    }
  }

  # can be used to add groups to tokens and assign roles - but no correlation between role and group!
  # Defines roles within the app - mainly required for the backend,
  # but also used by the backendAPI to impersonate the user to access the Microsoft Graph API
  # and/or to access the backendAPI from postman/thunderclient
  # Here's how to assign these roles to users and groups:
  # https://learn.microsoft.com/en-us/entra/identity-platform/howto-add-app-roles-in-apps#assign-users-and-groups-to-microsoft-entra-roles
  app_role {
    allowed_member_types = ["User"] # can also be ["User", "Application"], meaning 'User' or 'Application' on the Azure Tenant.
    description          = "Admins can manage the whole application"
    display_name         = "Admin"
    enabled              = true
    id                   = random_uuid.RoleAdmin.result
    value                = "Admin"
  }

  app_role {
    allowed_member_types = ["User"] # can also be ["User", "Application"], meaning 'User' or 'Application' on the Azure Tenant.
    description          = "Users can access the content of the application"
    display_name         = "User" # Visible to end user
    enabled              = true
    id                   = random_uuid.RoleUser.result
    value                = "User" # could be comething like "User.Write" or "User.Read"
  }

  # Grants the app access to the Microsoft Graph API with specific roles and scopes
  # MS Graph access to openid, profile and User.Read
  # Note: this is for on-behalf-of flow from backendAPI to MS Graph API
  # The frontend gets those scopes directly from MS Graph when user logs in and sscopes are requested there.
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

    # User.ReadWrite
    # resource_access {
    #   id   = "b4e74841-8e56-480b-be8b-910348b18b4c" 
    #   type = "Scope"
    # }

    # Additional:
    # Calendars.ReadWrite - delegated
    resource_access {
      id   = "1ec239c2-d7c9-4623-a91a-a9775856bb36"
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

    # Sites.Read.All - delegated
    # resource_access {
    #   id   = ""
    #   type = "Scope"
    # }

    # Sites.ReadWrite.All - delegated
    # resource_access {
    #   id   = ""
    #   type = "Scope"
    # }

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
      id   = "b340eb25-3456-403f-be2f-af7a0d370277"
      type = "Scope"
    }

    # Team.ReadBasic.All - delegated
    resource_access {
      id   = "485be79e-c497-4b35-9400-0e3fa7f2a5d4"
      type = "Scope"
    }
  }

  tags = [var.costcenter, var.owner_name, terraform.workspace]
}

# creates a client secret - which the backend uses for it's msal-client for user-impersonation to access MS Graph API
resource "azuread_application_password" "backendAPIClientSecret" {
  application_id = azuread_application.backendAPI.id
  end_date       = "2046-01-31T23:59:59Z"
}

resource "azuread_application_identifier_uri" "backendAPIURI" {
  application_id = azuread_application.backendAPI.id
  identifier_uri = "api://${azuread_application.backendAPI.client_id}"
}

resource "azuread_service_principal" "backendAPI" { # TBD: consider renaming into "backendAPI"
  client_id                    = azuread_application.backendAPI.client_id
  app_role_assignment_required = false
  description                  = "Service principal for the fullStackSandbox23 application"
  # owners                       = [data.azuread_client_config.current.object_id, var.owner_object_id]
  owners                       = [var.owner_object_id, var.developer_localhost_object_id, var.managed_identity_github_actions_object_id]
  notification_email_addresses = [var.budget_notification_email]
}

resource "azuread_application_pre_authorized" "preAuthorizeFrontendatBackend" {
  application_id       = azuread_application.backendAPI.id
  authorized_client_id = azuread_application.frontend.client_id

  # TBD: add all scopes, that frontend needs to access backendAPI:
  permission_ids = [
    random_uuid.ScopeApiRead.result,
    random_uuid.ScopeApiWrite.result,
    random_uuid.ScopeSocketio.result,
  ]
}

resource "azuread_application" "frontend" {
  display_name = "${var.project_name}-frontend-${terraform.workspace}"
  description  = "Frontend for the ${var.project_name} application"
  # owners                  = [data.azuread_client_config.current.object_id, var.owner_object_id]
  owners                  = [var.owner_object_id, var.developer_localhost_object_id, var.managed_identity_github_actions_object_id]
  prevent_duplicate_names = true
  sign_in_audience        = "AzureADMyOrg"
  group_membership_claims = ["ApplicationGroup"]


  # For OAuth2 Authorization Code Flow / on-behalf-of flow with ConfidentialClientApplication from @azure/msal-node
  web {
    redirect_uris = (terraform.workspace == "dev" ?
      [
        "http://localhost:8661/oauth/callback",
        "https://${azurerm_container_app.FrontendSvelteContainer.ingress[0].fqdn}/oauth/callback",
      ] :
      [
        "https://${azurerm_container_app.FrontendSvelteContainer.ingress[0].fqdn}/oauth/callback"
      ]
    )
  }
  # or
  # For Oauth2 Authorization Code Flow with PKCE from using PublicClientApplication from @azure/msal-browser
  # single_page_application {
  #   redirect_uris = ["http://localhost:8661/oauth/callback", "https://${azurerm_container_app.FrontendSvelteContainer.ingress[0].fqdn}:${azurerm_container_app.FrontendSvelteContainer.ingress[0].target_port}/oauth/callback"]
  # }

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

  tags = [var.costcenter, var.owner_name, terraform.workspace]
}

# creates a client secret for the frontend for the web application, which uses it for msal-client-node:
resource "azuread_application_password" "frontendClientSecret" {
  application_id = azuread_application.frontend.id
  end_date       = "2046-01-31T23:59:59Z"
}


resource "azuread_application" "developerClients" {
  display_name            = "${var.project_name}-developerClients-${terraform.workspace}"
  description             = "Developer clients for the ${var.project_name} application"
  owners                  = [var.owner_object_id, var.developer_localhost_object_id, var.managed_identity_github_actions_object_id]
  prevent_duplicate_names = true
  sign_in_audience        = "AzureADMyOrg"
  group_membership_claims = ["ApplicationGroup"]

  web {
    redirect_uris = [
      # ThunderClient:
      "https://www.thunderclient.com/oauth/callback",
      # Postman:
      "https://oauth.pstmn.io/v1/callback",
    ]
  }

  single_page_application {
    redirect_uris = (terraform.workspace == "dev" ?
      # OpenAPI (former SwaggerUI) interface served from backendAPI:
      [
        "http://localhost:8660/docs/oauth2-redirect",
        "https://${azurerm_container_app.BackendAPIContainer.ingress[0].fqdn}/docs/oauth2-redirect",
      ] :
      [
        "https://${azurerm_container_app.BackendAPIContainer.ingress[0].fqdn}/docs/oauth2-redirect",
      ]
    )
  }

  tags = [var.costcenter, var.owner_name, terraform.workspace]
}

# creates a client secret for the developer clients, which are used in Postman and Thunderclient
# TBD: consider different secrets for those two clients and one for each developer?
resource "azuread_application_password" "developerClientsSecret" {
  application_id = azuread_application.developerClients.id
  end_date       = "2046-01-31T23:59:59Z"
}

resource "azuread_application" "postgresAdmin" {
  count                   = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  display_name            = "${var.project_name}-pgAdmin-${terraform.workspace}"
  description             = "Postgres Admin (pgAdmin) for admin access to ${var.project_name} database"
  owners                  = [var.owner_object_id, var.developer_localhost_object_id, var.managed_identity_github_actions_object_id]
  prevent_duplicate_names = true
  sign_in_audience        = "AzureADMyOrg"
  group_membership_claims = ["ApplicationGroup"]

  lifecycle {
    ignore_changes = [web, app_role]
  }

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

    # email:
    resource_access {
      id   = "64a6cdd6-aab1-4aaf-94b8-3cc8405e90d0"
      type = "Scope"
    }
  }

  tags = [var.costcenter, var.owner_name, terraform.workspace]
}

resource "azuread_application_redirect_uris" "postgresAdminOAuthRedirectURI" {
  count          = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  application_id = azuread_application.postgresAdmin[0].id
  type           = "Web"


  redirect_uris = (terraform.workspace == "dev" ?
    [
      "https://${azurerm_container_app.postgresAdmin[0].ingress[0].fqdn}/oauth2/authorize",
      "http://localhost:5533/oauth2/authorize",
    ]
    :
    [
      "https://${azurerm_container_app.postgresAdmin[0].ingress[0].fqdn}/oauth2/authorize",
    ]
  )
}

resource "azuread_application_password" "postgresAdminSecret" {
  count          = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  application_id = azuread_application.postgresAdmin[0].id
  end_date       = "2046-01-31T23:59:59Z"
}

resource "azuread_service_principal" "postgresAdmin" {
  count       = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  client_id   = azuread_application.postgresAdmin[0].client_id
  description = "Service principal for pgAdmin access to ${var.project_name} database"
  owners      = [var.owner_object_id, var.developer_localhost_object_id, var.managed_identity_github_actions_object_id]
  # Enabling app_role_assignement requires the Azure Tenant Admin to assign the application to a user
  # otherwise the application does not issue tokens and Admin consent is required.
  # app_role_assignment_required = true 
  notification_email_addresses = [var.pgadmin_default_email]
  feature_tags {
    hide = true
  }
}

# Here's how to assign these roles to users and groups:
# https://learn.microsoft.com/en-us/entra/identity-platform/howto-add-app-roles-in-apps#assign-users-and-groups-to-microsoft-entra-roles
resource "azuread_application_app_role" "postgresAdminAppRoleAdmin" {
  count                = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  application_id       = azuread_application.postgresAdmin[0].id
  allowed_member_types = ["User"] # can also be ["User", "Application"], meaning 'User' or 'Application' on the Azure Tenant.
  description          = "Database Admins can manage the database via pgAdmin"
  display_name         = "Admin"
  role_id              = random_uuid.pgAdminRoleAdmin[0].result
  value                = "Admin"
}
