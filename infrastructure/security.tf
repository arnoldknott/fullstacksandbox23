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
      "Get", "Create", "Delete", "Update"
    ]

    key_permissions = [
      "Get", "Create", "Delete", "Update"
    ]

    secret_permissions = [
      "Get", "Set", "Delete", "Recover"
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
  value        = azurerm_container_app.BackendContainer.name
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "azurerm_key_vault_secret" "backendFqdn" {
  name         = "backend-fqdn"
  value        = azurerm_container_app.BackendContainer.ingress[0].fqdn
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

resource "random_password" "redisWorkerPassword" {
  length  = 32
  special = false
}
resource "azurerm_key_vault_secret" "redisWorkerPassword" {
  name         = "redis-worker-password"
  value        = random_password.redisWorkerPassword.result
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

# APP_REG_CLIENT_ID: is FRONTEND!
resource "azurerm_key_vault_secret" "app-reg-client-id" {
  name         = "app-reg-client-id"
  value        = azuread_application.frontend.client_id
  key_vault_id = azurerm_key_vault.keyVault.id
}

# AZURE_CLIENT_ID: is BACKEND!
resource "azurerm_key_vault_secret" "azure-client-id" {
  name         = "azure-client-id"
  value        = azuread_application.backendAPI.client_id
  key_vault_id = azurerm_key_vault.keyVault.id
}

resource "azurerm_key_vault_secret" "app-client-secret" {
  name         = "app-client-secret"
  value        = azuread_application_password.frontendClientSecret.value
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

# backend-client-secret is the secret for the backend API, to act on behalf of the user logged in in the frontend
resource "azurerm_key_vault_secret" "back-client-secret" {
  name         = "back-client-secret"
  value        = azuread_application_password.backendAPIClientSecret.value
  key_vault_id = azurerm_key_vault.keyVault.id
}

# resource "azurerm_key_vault_secret" "pgadminDefaultEmail" {
#   count = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
#   name         = "pgadmin-default-email"
#   value        = var.owner
#   key_vault_id = azurerm_key_vault.keyVault.id
# }

# resource "random_password" "pgadminDefaultPassword" {
#   count = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
#   length  = 24
#   special = false
# }
# resource "azurerm_key_vault_secret" "pgadminDefaultPassword" {
#   count = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
#   name         = "pgadmin-default-password"
#   value        = random_password.pgadminDefaultPassword[0].result
#   key_vault_id = azurerm_key_vault.keyVault.id
# }

# Container apps need to have the secrets in the key vault to be able to use them.
# data "azurerm_key_vault_secrets" "keyVaultAllSecrets" {
#   key_vault_id = azurerm_key_vault.keyVault.id
# }

# data "azurerm_key_vault_secret" "keyVaultSecret" {
#   for_each     = toset(data.azurerm_key_vault_secrets.keyVaultAllSecrets.names)
#   name         = each.key
#   key_vault_id = azurerm_key_vault.keyVault.id
# }