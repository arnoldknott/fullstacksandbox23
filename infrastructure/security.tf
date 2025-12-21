resource "azurerm_user_assigned_identity" "frontendIdentity" {
  name                = "${var.project_name}-frontendIdentity-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

resource "azurerm_user_assigned_identity" "backendIdentity" {
  name                = "${var.project_name}-backendIdentity-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

# resource "azurerm_user_assigned_identity" "postgresIdentity" {
#   name                = "${var.project_name}-postgresIdentity-${terraform.workspace}"
#   resource_group_name = azurerm_resource_group.resourceGroup.name
#   location            = azurerm_resource_group.resourceGroup.location

#   tags = {
#     Costcenter  = var.costcenter
#     Owner       = var.owner_name
#     Environment = terraform.workspace
#   }
# }

resource "azurerm_user_assigned_identity" "pgadminIdentity" {
  name                = "${var.project_name}-pgadminIdentity-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

resource "azurerm_user_assigned_identity" "redisIdentity" {
  name                = "${var.project_name}-redisIdentity-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

# resource "azurerm_user_assigned_identity" "mongodbIdentity" {
#   name                = "${var.project_name}-mongodbIdentity-${terraform.workspace}"
#   resource_group_name = azurerm_resource_group.resourceGroup.name
#   location            = azurerm_resource_group.resourceGroup.location

#   tags = {
#     Costcenter  = var.costcenter
#     Owner       = var.owner_name
#     Environment = terraform.workspace
#   }
# }

resource "azurerm_user_assigned_identity" "workerIdentity" {
  name                = "${var.project_name}-workerIdentity-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

resource "azurerm_key_vault" "keyVault" {
  name                        = "${var.project_short_name}-keyVault-${terraform.workspace}"
  location                    = azurerm_resource_group.resourceGroup.location
  resource_group_name         = azurerm_resource_group.resourceGroup.name
  enabled_for_disk_encryption = true
  tenant_id                   = var.azure_tenant_id
  soft_delete_retention_days  = 30
  purge_protection_enabled    = false

  sku_name = "standard"

  access_policy {
    tenant_id = var.azure_tenant_id
    object_id = var.owner_object_id

    certificate_permissions = [
      "Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", "Purge", "Recover", "Restore", "SetIssuers", "Update"
    ]

    key_permissions = [
      "Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", "List", "Recover", "Restore", "Sign", "UnwrapKey", "Update", "Verify", "WrapKey", "Purge", "Release", "Rotate", "GetRotationPolicy", "SetRotationPolicy"
    ]

    secret_permissions = [
      "Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"
    ]

    storage_permissions = [
      "Backup", "Delete", "DeleteSAS", "Get", "GetSAS", "List", "ListSAS", "Recover", "RegenerateKey", "Restore", "Set", "SetSAS", "Update"
    ]
  }

  # Allow the apps running terraform to write secrets from the vault for configuring the container apps:
  # - container on developer localhost:
  access_policy {
    tenant_id = var.azure_tenant_id
    object_id = var.developer_localhost_object_id

    certificate_permissions = [
      "Get", "Create", "Delete", "Update", "Purge"
    ]

    key_permissions = [
      "Get", "Create", "Delete", "Update", "Purge"
    ]

    secret_permissions = [
      "Get", "Set", "Delete", "Recover", "Purge"
    ]
  }

  # - github actions managed identity:
  access_policy {
    tenant_id = var.azure_tenant_id
    object_id = var.managed_identity_github_actions_object_id

    certificate_permissions = [
      "Get", "Create", "Delete", "Update", "Purge"
    ]

    key_permissions = [
      "Get", "Create", "Delete", "Update", "Purge"
    ]

    secret_permissions = [
      "Get", "Set", "Delete", "Recover", "Purge"
    ]
  }

  access_policy {
    tenant_id = var.azure_tenant_id
    object_id = azurerm_user_assigned_identity.backendIdentity.principal_id

    certificate_permissions = [
      "Get"
    ]

    key_permissions = [
      "Get"
    ]

    secret_permissions = [
      "Get"
    ]
  }

  access_policy {
    tenant_id = var.azure_tenant_id
    object_id = azurerm_user_assigned_identity.frontendIdentity.principal_id

    certificate_permissions = [
      "Get"
    ]

    key_permissions = [
      "Get"
    ]

    secret_permissions = [
      "Get"
    ]
  }

  # access_policy {
  #   tenant_id = var.azure_tenant_id
  #   object_id = azurerm_user_assigned_identity.postgresIdentity.principal_id

  #   certificate_permissions = [
  #     "Get"
  #   ]

  #   key_permissions = [
  #     "Get"
  #   ]

  #   secret_permissions = [
  #     "Get"
  #   ]
  # }

  access_policy {
    tenant_id = var.azure_tenant_id
    object_id = azurerm_user_assigned_identity.pgadminIdentity.principal_id

    # certificate_permissions = [
    #   "Get"
    # ]

    # key_permissions = [
    #   "Get"
    # ]

    secret_permissions = [
      "Get"
    ]
  }

  access_policy {
    tenant_id = var.azure_tenant_id
    object_id = azurerm_user_assigned_identity.redisIdentity.principal_id

    certificate_permissions = [
      "Get"
    ]

    key_permissions = [
      "Get"
    ]

    secret_permissions = [
      "Get"
    ]
  }

  # access_policy {
  #   tenant_id = var.azure_tenant_id
  #   object_id = azurerm_user_assigned_identity.mongodbIdentity.principal_id

  #   certificate_permissions = [
  #     "Get"
  #   ]

  #   key_permissions = [
  #     "Get"
  #   ]

  #   secret_permissions = [
  #     "Get"
  #   ]
  # }

  access_policy {
    tenant_id = var.azure_tenant_id
    object_id = azurerm_user_assigned_identity.workerIdentity.principal_id

    certificate_permissions = [
      "Get"
    ]

    key_permissions = [
      "Get"
    ]

    secret_permissions = [
      "Get"
    ]
  }


  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }

}

resource "azurerm_key_vault_secret" "keyvaultHealth" {
  name         = "keyvault-health"
  value        = "ok, keyvault, ${azurerm_key_vault.keyVault.name}, ${terraform.workspace}"
  key_vault_id = azurerm_key_vault.keyVault.id
}

# implemented as secret to break circular dpendency
# between backend and frontend container app
# but it's no really a secret!
resource "azurerm_key_vault_secret" "backendHost" {
  name         = "backend-host"
  value        = azurerm_container_app.BackendAPIContainer.name
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "azurerm_key_vault_secret" "backendFqdn" {
  name         = "backend-fqdn"
  value        = azurerm_container_app.BackendAPIContainer.ingress[0].fqdn
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "random_string" "postgresUser" {
  length  = 12
  special = false
}
resource "azurerm_key_vault_secret" "postgresUser" {
  name         = "postgres-user"
  value        = random_string.postgresUser.result
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "random_password" "postgresPassword" {
  length  = 24
  special = false
}
resource "azurerm_key_vault_secret" "postgresPassword" {
  name         = "postgres-password"
  value        = random_password.postgresPassword.result
  key_vault_id = azurerm_key_vault.keyVault.id
}

# TBD: change to env variable in container - no need to make secret
resource "azurerm_key_vault_secret" "postgresHost" {
  name         = "postgres-host"
  value        = "${var.project_short_name}-postgres-${terraform.workspace}.postgres.database.azure.com" #azurerm_private_dns_zone.privateDNSZone.name
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "random_password" "redisPassword" {
  length  = 32
  special = false
}
resource "azurerm_key_vault_secret" "redisPassword" {
  name         = "redis-password"
  value        = random_password.redisPassword.result
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "random_password" "redisSessionPassword" {
  length  = 32
  special = false
}
resource "azurerm_key_vault_secret" "redisSessionPassword" {
  name         = "redis-session-password"
  value        = random_password.redisSessionPassword.result
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "random_password" "redisSocketioPassword" {
  length  = 32
  special = false
}
resource "azurerm_key_vault_secret" "redisSocketioPassword" {
  name         = "redis-socketio-password"
  value        = random_password.redisSocketioPassword.result
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "random_password" "redisCeleryPassword" {
  length  = 32
  special = false
}
resource "azurerm_key_vault_secret" "redisCeleryPassword" {
  name         = "redis-celery-password"
  value        = random_password.redisCeleryPassword.result
  key_vault_id = azurerm_key_vault.keyVault.id
}

# Socket.io admin interface - user name and password to non-zero values,
# enables the admin interface through https://admin.socket.io/#/
# use advanced settings options at log in to set the correct path to the socket.io server
resource "azurerm_key_vault_secret" "socketioAdminUsername" {
  name         = "socketio-admin-username"
  value        = ""
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "azurerm_key_vault_secret" "socketioAdminPassword" {
  name         = "socketio-admin-password"
  value        = ""
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "azurerm_key_vault_secret" "frontendSvelteClientId" {
  name         = "frontend-svelte-client-id"
  value        = azuread_application.frontend.client_id
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "azurerm_key_vault_secret" "frontendSvelteClientSecret" {
  name         = "frontend-svelte-client-secret"
  value        = azuread_application_password.frontendClientSecret.value
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "azurerm_key_vault_secret" "developerClientsClientId" {
  name         = "developer-clients-client-id"
  value        = azuread_application.developerClients.client_id
  key_vault_id = azurerm_key_vault.keyVault.id
}


resource "azurerm_key_vault_secret" "backendApiClientId" {
  name         = "backend-api-client-id"
  value        = azuread_application.backendAPI.client_id
  key_vault_id = azurerm_key_vault.keyVault.id
}


resource "azurerm_key_vault_secret" "api-scope" {
  name         = "api-scope"
  value        = azuread_application.backendAPI.client_id
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "azurerm_key_vault_secret" "azure-tenant-id" {
  name         = "azure-tenant-id"
  value        = var.azure_tenant_id
  key_vault_id = azurerm_key_vault.keyVault.id
}

# backend uses for it for its msal-client for user-impersonation to access MS Graph API
resource "azurerm_key_vault_secret" "back-client-secret" {
  name         = "back-client-secret"
  value        = azuread_application_password.backendAPIClientSecret.value
  key_vault_id = azurerm_key_vault.keyVault.id
}

# Stores secret for developer clients, which are used in Postman and Thunderclient
# (not used programmatically anywhere else for now)
resource "azurerm_key_vault_secret" "developer-clients-secret" {
  name         = "developer-clients-secret"
  value        = azuread_application_password.developerClientsSecret.value
  key_vault_id = azurerm_key_vault.keyVault.id
}

################
# TBD: comment after switching to OAuth2 login only
resource "azurerm_key_vault_secret" "pgadminDefaultEmail" {
  count        = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  name         = "pgadmin-default-email"
  value        = var.pgadmin_default_email
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "random_password" "pgadminDefaultPassword" {
  count   = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  length  = 24
  special = false
}
resource "azurerm_key_vault_secret" "pgadminDefaultPassword" {
  count        = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  name         = "pgadmin-default-password"
  value        = random_password.pgadminDefaultPassword[0].result
  key_vault_id = azurerm_key_vault.keyVault.id
}
################

resource "random_password" "pgadminMasterPassword" {
  count   = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  length  = 24
  special = false
}

resource "azurerm_key_vault_secret" "pgadminMasterPassword" {
  count        = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  name         = "pgadmin-master-password"
  value        = random_password.pgadminMasterPassword[0].result
  key_vault_id = azurerm_key_vault.keyVault.id
}

locals {
  count                 = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  # This is predictive and resolves circular conflict between container app and key vault secret:
  # TBD: use this prediction also for backend and frontend apps to remove circular dependencies instead of saving the fqdn's as secrets.
  pgadmin_fqdn = "${var.project_short_name}-pgadmin-${terraform.workspace}.${azurerm_container_app_environment.ContainerEnvironment.default_domain}"
  # or using this below:
  # 'OAUTH2_LOGOUT_URL': 'https://login.microsoftonline.com/${var.azure_tenant_id}/oauth2/v2.0/logout?post_logout_redirect_uri=https://${var.project_short_name}-pgadmin-${terraform.workspace}.${azurerm_container_app_environment.ContainerEnvironment.default_domain}',
  pgadmin_oauth2_config = <<EOT
[{
  'OAUTH2_NAME': 'EntraID',
  'OAUTH2_DISPLAY_NAME': 'Microsoft Entra ID',
  'OAUTH2_CLIENT_ID': '${azuread_application.postgresAdmin[0].client_id}',
  'OAUTH2_CLIENT_SECRET': '${azuread_application_password.postgresAdminSecret[0].value}',
  'OAUTH2_TOKEN_URL': 'https://login.microsoftonline.com/${var.azure_tenant_id}/oauth2/v2.0/token',
  'OAUTH2_AUTHORIZATION_URL': 'https://login.microsoftonline.com/${var.azure_tenant_id}/oauth2/v2.0/authorize',
  'OAUTH2_SERVER_METADATA_URL': 'https://login.microsoftonline.com/${var.azure_tenant_id}/v2.0/.well-known/openid-configuration',
  'OAUTH2_API_BASE_URL': 'https://graph.microsoft.com/oidc/',
  'OAUTH2_USERINFO_ENDPOINT': 'userinfo',
  'OAUTH2_SCOPE': 'openid profile email',
  'OAUTH2_ADDITIONAL_CLAIMS': {'roles': ['Admin']},
  'OAUTH2_LOGOUT_URL': 'https://login.microsoftonline.com/${var.azure_tenant_id}/oauth2/v2.0/logout?post_logout_redirect_uri=https://${local.pgadmin_fqdn}',
  'OAUTH2_CHALLENGE_METHOD': 'S256',
  'OAUTH2_RESPONSE_TYPE': 'code',
  'OAUTH2_USERNAME_CLAIM': 'preferred_username',
  'OAUTH2_ICON': 'fa-microsoft',
  'OAUTH2_BUTTON_COLOR': '#00A4EF'
}]
EOT
}


resource "azurerm_key_vault_secret" "pgadminOauth2Config" {
  count        = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  name         = "pgadmin-oauth2-config"
  value        = local.pgadmin_oauth2_config
  key_vault_id = azurerm_key_vault.keyVault.id
}

# Container apps need to have the secrets in the key vault to be able to use them.
# data "azurerm_key_vault_secrets" "keyVaultAllSecrets" {
#   key_vault_id = azurerm_key_vault.keyVault.id
# }

# data "azurerm_key_vault_secret" "keyVaultSecret" {
#   for_each     = toset(data.azurerm_key_vault_secrets.keyVaultAllSecrets.names)
#   name         = each.key
#   key_vault_id = azurerm_key_vault.keyVault.id
# }