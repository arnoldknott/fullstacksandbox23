# resource "random_uuid" "apiURI" {}
resource "random_uuid" "UuidScope1" {}
resource "random_uuid" "UuidScope2" {}
resource "random_uuid" "UuidScope3" {}
resource "random_uuid" "UuidRole1" {}     # Used for admins in backend
resource "random_uuid" "userGroupUUID" {} # Used for users in backend
# resource "random_uuid" "UuidRole2" {}
# resource "random_uuid" "UuidRole3" {}
# resource "random_uuid" "UuidRole4" {}
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
      admin_consent_description  = "Allow the application to read from the test user and session handling API on behalf of the signed-in user. See owner property for more information."
      admin_consent_display_name = "Read from test user and session handling API"
      enabled                    = true
      id                         = random_uuid.UuidScope2.result
      type                       = "User"
      user_consent_description   = "Allow the application to read from the test user and session handling API on your behalf."
      user_consent_display_name  = "Read access to test user and session handling API"
      value                      = "api.read"
    }

    oauth2_permission_scope {
      admin_consent_description  = "Allow the application to write to the test user and session handling API on behalf of the signed-in user. See owner property for more information."
      admin_consent_display_name = "Write to test user and session handling API"
      enabled                    = true
      id                         = random_uuid.UuidScope3.result
      type                       = "User"
      user_consent_description   = "Allow the application to write to the test user and session handling API on your behalf."
      user_consent_display_name  = "Write access to test user and session handling API"
      value                      = "api.write"
    }

    # add further scopes here:
    # add artificial.read, artificial.write, mapped_account.read, mapped_account.write, ...

  }

  # can be used to add groups to tokens and assign roles - but no correleation between role and group!
  # Defines roles within the app - mainnly required for the backend,
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


  # Fine graind access in code - as there is no correlation in the token for which role in which group!
  # app_role {
  #   allowed_member_types = ["User"]
  #   description          = "Teachers can manage their courses"
  #   display_name         = "Teacher"
  #   enabled              = true
  #   id                   = random_uuid.UuidRole2.result
  #   value                = "Teacher"
  # }

  # app_role {
  #   allowed_member_types = ["User"]
  #   description          = "Guest lecturers can view parts of the course"
  #   display_name         = "Guest Lecturer"
  #   enabled              = true
  #   id                   = random_uuid.UuidRole3.result
  #   value                = "GuestLecturer"
  # }

  # app_role {
  #   allowed_member_types = ["User"]
  #   description          = "Students can access their courses"
  #   display_name         = "Student"
  #   enabled              = true
  #   id                   = random_uuid.UuidRole4.result
  #   value                = "Student"
  # }

  # app_role {
  #   allowed_member_types = ["User"]
  #   description          = "Guest students can view courses"
  #   display_name         = "Guest Student"
  #   enabled              = true
  #   id                   = random_uuid.UuidRole5.result
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

    resource_access {
      id   = "37f7f235-527c-4136-accd-4a02d197296e"
      type = "Scope"
    }
    resource_access {
      id   = "14dad69e-099b-42c9-810b-d002981feec1"
      type = "Scope"
    }
    resource_access {
      id   = "e1fe6dd8-ba31-4d61-89e7-88639da4683d"
      type = "Scope"
    }
  }

  # TBD: consider adding for enabling swaggerUI authentication - change the host names for stage and prod:
  # single_page_application {
  #   redirect_uris = [
  #     "http://localhost:8660/docs/oauth2-redirect"
  #   ]
  # }


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
        # "http://localhost:8661/oauth/tokens",
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
