
resource "azurerm_storage_account" "storage" {
  name                             = "${var.project_short_name}storage${terraform.workspace}"
  resource_group_name              = azurerm_resource_group.resourceGroup.name
  location                         = azurerm_resource_group.resourceGroup.location
  account_tier                     = "Standard"
  account_replication_type         = "LRS"
  cross_tenant_replication_enabled = false

  # This would lock the terraform script and the github-hosted runner out! Don't activate for now!
  # network_rules {
  #   default_action = "Deny"
  #   bypass        = ["Metrics", "Logging", "AzureServices"]
  # private_link_access = {
  #   endpoint_resource_id = azurerm_subnet.subnetFileStorage.id
  # }
  #   virtual_network_subnet_ids = [azurerm_subnet.subnetFileStorage.id]
  # }

  # add AD authnetication and allow the following RBAC access:
  # Terraform script: vars.azure_sp_object_id
  # Github-hosted runner: azurerm_service_principal.GithubActionsServicePrincipal.?? or azurerm_user_assigned_identity.GithubActionsManagedIdentity.???
  # backendAPI app registration: azurerm_service_principal.terraformServicePrincipal.???
  # backendAPI container app: azurerm_user_assigned_identity.backendIdentity

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

resource "azurerm_postgresql_flexible_server" "postgresServer" {
  name                          = "${var.project_short_name}-postgres-${terraform.workspace}"
  resource_group_name           = azurerm_resource_group.resourceGroup.name
  location                      = azurerm_resource_group.resourceGroup.location
  sku_name                      = "B_Standard_B1ms"
  version                       = "16"
  public_network_access_enabled = false

  lifecycle {
    ignore_changes = [zone]
  }

  administrator_login    = random_string.postgresUser.result
  administrator_password = random_password.postgresPassword.result

  # TBD: change login to Microsoft Entra AD
  # authentication {
  #   active_directory_auth_enabled = true
  #   # password_auth_enabled         = false # consider adding this - then no need for admin password above - but how does the backend get to the database then? RBAC?
  #   tenant_id                     = data.azurerm_client_config.current.tenant_id
  # }

  delegated_subnet_id = azurerm_subnet.subnetPostgres.id
  private_dns_zone_id = azurerm_private_dns_zone.privateDNSZone.id

  backup_retention_days = 31
  storage_mb            = 131072

  maintenance_window {
    day_of_week  = 0
    start_hour   = 1
    start_minute = 23
  }

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}
# TBD: consider setting azurerm_postgresql_flexible_server_active_directory_administrator
# TBD: consider adding the empty database resource azurerm_postgresql_flexible_server_database

resource "azurerm_postgresql_flexible_server_database" "postgresDatabase" {
  name      = "${terraform.workspace}_db" # needs to match the github environment variable POSTGRES_DB
  server_id = azurerm_postgresql_flexible_server.postgresServer.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# resource "random_uuid" "uuidPostgresAccessShare" {}
# resource "azurerm_storage_share" "postgresData" {
#   name                 = "${var.project_short_name}-postgresdata-${terraform.workspace}"
#   storage_account_id   = azurerm_storage_account.storage.id
#   quota                = 100 #TBD: increase for production and keep an eye on cost!
#   acl {
#     id = random_uuid.uuidPostgresAccessShare.result
#     access_policy {
#       permissions = "rwdl"
#     }
#   }
# }

resource "azurerm_storage_share" "redisData" {
  name               = "${var.project_short_name}-redisdata-${terraform.workspace}"
  storage_account_id = azurerm_storage_account.storage.id
  quota              = 10 #TBD: increase for production and keep an eye on cost!
}

# using .url insted of .id, due to bug:
# https://github.com/hashicorp/terraform-provider-azurerm/issues/28032
resource "azurerm_storage_share_file" "redisEntrypoint" {
  name             = "entrypoint.sh"
  storage_share_id = azurerm_storage_share.redisData.url
  source           = "./cacheRedis/entrypoint.sh"
}

resource "azurerm_storage_share_file" "redisConf" {
  name             = "redis.conf"
  storage_share_id = azurerm_storage_share.redisData.url
  source           = "./cacheRedis/redis.conf"
}

resource "azurerm_storage_share_file" "redisConfFull" {
  name             = "redis-full.conf"
  storage_share_id = azurerm_storage_share.redisData.url
  source           = "./cacheRedis/redis-full.conf"
}

resource "azurerm_storage_share_file" "redisUsersTemplate" {
  name             = "users_template.acl"
  storage_share_id = azurerm_storage_share.redisData.url
  source           = "./cacheRedis/users_template.acl"
}


# resource "azurerm_storage_share" "mongodbData" {
#   name                 = "${var.project_short_name}-mongodbdata-${terraform.workspace}"
#   storage_account_id   = azurerm_storage_account.storage.id
#   quota                = 10 #TBD: increase for production and keep an eye on cost!
# }

resource "azurerm_storage_share" "applicationData" {
  name               = "${var.project_short_name}-applicationdata-${terraform.workspace}"
  storage_account_id = azurerm_storage_account.storage.id
  quota              = 100 #TBD: increase for production and keep an eye on cost!
}

# Backup:

resource "azurerm_recovery_services_vault" "recoveryServiceVault" {
  name                          = "${var.project_name}-recoveryServiceVault-${terraform.workspace}"
  resource_group_name           = azurerm_resource_group.resourceGroup.name
  location                      = azurerm_resource_group.resourceGroup.location
  sku                           = "Standard"
  storage_mode_type             = "LocallyRedundant"
  immutability                  = "Disabled"
  public_network_access_enabled = true
  soft_delete_enabled           = true


  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

resource "azurerm_backup_container_storage_account" "backupContainer" {
  resource_group_name = azurerm_resource_group.resourceGroup.name
  recovery_vault_name = azurerm_recovery_services_vault.recoveryServiceVault.name
  storage_account_id  = azurerm_storage_account.storage.id
}

resource "azurerm_backup_policy_file_share" "backupDatabasePolicy" {
  name                = "${var.project_name}-backupDatabasePolicy-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  recovery_vault_name = azurerm_recovery_services_vault.recoveryServiceVault.name

  timezone = "UTC"

  backup {
    frequency = "Daily"
    time      = "04:00"
  }

  retention_daily {
    # 14 weeks:
    count = 98
  }

  # retention_monthly {
  #   count = 12
  #   weekdays = ["Sunday"]
  #   weeks = ["Last"]
  # }

  # retention_yearly {
  #   count = 6
  #   months = ["December"]
  #   days = [31]
  # }
}

resource "azurerm_backup_policy_file_share" "backupCachePolicy" {
  name                = "${var.project_name}-backupCachePolicy-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  recovery_vault_name = azurerm_recovery_services_vault.recoveryServiceVault.name

  timezone = "UTC"

  backup {
    frequency = "Daily"
    time      = "04:00"
  }

  retention_daily {
    count = 30
  }

  # retention_weekly {
  #   count = 13
  #   weekdays = ["Saturday",]
  # }

  # retention_monthly {
  #   count = 4
  #   weekdays = ["Sunday",]
  #   weeks = ["Last",]
  # }
}


# resource "azurerm_backup_protected_file_share" "enablePostgresBackup" {
#   resource_group_name       = azurerm_resource_group.resourceGroup.name
#   recovery_vault_name       = azurerm_recovery_services_vault.recoveryServiceVault.name
#   source_storage_account_id = azurerm_backup_container_storage_account.backupContainer.storage_account_id
#   source_file_share_name    = azurerm_storage_share.postgresData.name
#   backup_policy_id          = azurerm_backup_policy_file_share.backupDatabasePolicy.id
# }

resource "azurerm_backup_protected_file_share" "enableRedisBackup" {
  resource_group_name       = azurerm_resource_group.resourceGroup.name
  recovery_vault_name       = azurerm_recovery_services_vault.recoveryServiceVault.name
  source_storage_account_id = azurerm_backup_container_storage_account.backupContainer.storage_account_id
  source_file_share_name    = azurerm_storage_share.redisData.name
  backup_policy_id          = azurerm_backup_policy_file_share.backupCachePolicy.id
}

# resource "azurerm_backup_protected_file_share" "enableMongodbBackup" {
#   resource_group_name       = azurerm_resource_group.resourceGroup.name
#   recovery_vault_name       = azurerm_recovery_services_vault.recoveryServiceVault.name
#   source_storage_account_id = azurerm_backup_container_storage_account.backupContainer.storage_account_id
#   source_file_share_name    = azurerm_storage_share.mongodbData.name
#   backup_policy_id          = azurerm_backup_policy_file_share.backupDatabasePolicy.id
# }

resource "azurerm_backup_protected_file_share" "enableApplicationDataBackup" {
  resource_group_name       = azurerm_resource_group.resourceGroup.name
  recovery_vault_name       = azurerm_recovery_services_vault.recoveryServiceVault.name
  source_storage_account_id = azurerm_backup_container_storage_account.backupContainer.storage_account_id
  source_file_share_name    = azurerm_storage_share.applicationData.name
  backup_policy_id          = azurerm_backup_policy_file_share.backupDatabasePolicy.id
}

### DECISSION ABOVE!
# ### DISCUSSION with myself below:

# # potentially together with:

# resource "???file_sync" "name" {

# }

# resource "***azure_backup" "name" {

# }

# ## OR ANOTHER SOLUTION FOR THE VAULT:

# resource "???azurerm_backup_vault" "name" {

# }

# ## CONCLUSION:
# # two ways to create backup: 
# # + azure recovery service vault
# # X azure backup vault
# # two ways to sync
# # X azure file sync
# # + azure backup
