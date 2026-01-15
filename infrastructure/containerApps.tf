resource "azurerm_log_analytics_workspace" "logAnalytics" {
  name                = "${var.project_name}-logAnalytics-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location
  sku                 = "PerGB2018"
}

resource "azurerm_container_app_environment" "ContainerEnvironment" {
  name                       = "${var.project_name}-containers-${terraform.workspace}"
  location                   = azurerm_resource_group.resourceGroup.location
  resource_group_name        = azurerm_resource_group.resourceGroup.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.logAnalytics.id
  infrastructure_subnet_id   = azurerm_subnet.subnetContainerapp.id

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

# resource "azurerm_container_app_environment_storage" "postgresDataConnect" {
#   name                         = "${var.project_short_name}-postgresdataconnect-${terraform.workspace}"
#   container_app_environment_id = azurerm_container_app_environment.ContainerEnvironment.id
#   account_name                 = azurerm_storage_account.storage.name
#   access_key                   = azurerm_storage_account.storage.primary_access_key
#   share_name                   = azurerm_storage_share.postgresData.name
#   access_mode                  = "ReadWrite"
# }

resource "azurerm_container_app_environment_storage" "redisDataConnect" {
  name                         = "${var.project_short_name}-redisdataconnect-${terraform.workspace}"
  container_app_environment_id = azurerm_container_app_environment.ContainerEnvironment.id
  account_name                 = azurerm_storage_account.storage.name
  access_key                   = azurerm_storage_account.storage.primary_access_key
  share_name                   = azurerm_storage_share.redisData.name
  access_mode                  = "ReadWrite"
}

# resource "azurerm_container_app_environment_storage" "mongodbDataConnect" {
#   name                         = "${var.project_short_name}-mongodbdataconnect-${terraform.workspace}"
#   container_app_environment_id = azurerm_container_app_environment.ContainerEnvironment.id
#   account_name                 = azurerm_storage_account.storage.name
#   access_key                   = azurerm_storage_account.storage.primary_access_key
#   share_name                   = azurerm_storage_share.mongodbData.name
#   access_mode                  = "ReadWrite"
# }

resource "azurerm_container_app_environment_storage" "applicationDataConnect" {
  name                         = "${var.project_short_name}-appdataconnect-${terraform.workspace}"
  container_app_environment_id = azurerm_container_app_environment.ContainerEnvironment.id
  account_name                 = azurerm_storage_account.storage.name
  access_key                   = azurerm_storage_account.storage.primary_access_key
  share_name                   = azurerm_storage_share.applicationData.name
  access_mode                  = "ReadWrite"
}

resource "azurerm_container_app_environment_storage" "adminDataConnect" {
  count                        = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  name                         = "${var.project_short_name}-admindataconnect-${terraform.workspace}"
  container_app_environment_id = azurerm_container_app_environment.ContainerEnvironment.id
  account_name                 = azurerm_storage_account.storage.name
  access_key                   = azurerm_storage_account.storage.primary_access_key
  share_name                   = azurerm_storage_share.adminData[0].name
  access_mode                  = "ReadWrite"
}

# stalled on 2024-01-12 in stage: https://fssb23-frontend-stage.gentlefield-715ad89b.northeurope.azurecontainerapps.io
resource "azurerm_container_app" "FrontendSvelteContainer" {
  name                         = "${var.project_short_name}-frontend-${terraform.workspace}"
  container_app_environment_id = azurerm_container_app_environment.ContainerEnvironment.id
  resource_group_name          = azurerm_resource_group.resourceGroup.name
  revision_mode                = "Single"

  # Never change the imaage of the container, as this is done in github actions!
  lifecycle {
    ignore_changes = [template[0].container[0].image] # secret, ingress
  }

  template {
    container {
      name  = "frontend"
      image = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
      # Frontend container is close to limit with 0.5Gi!
      cpu    = 0.5   #0.25
      memory = "1Gi" #"0.5Gi"
      # Due to cyclic dependency, backend origin is moved into a keyvault secret.
      # env {
      #   name = "BACKEND_HOST"
      #   # value = azurerm_container_app.BackendAPIContainer.ingress[0].fqdn
      #   value = azurerm_container_app.BackendAPIContainer.name
      # }
      // required for keyvault access due to "working with AKS pod-identity" - see here:
      // https://learn.microsoft.com/en-us/javascript/api/@azure/identity/managedidentitycredential?view=azure-node-latest
      env {
        name  = "AZ_CLIENT_ID"
        value = azurerm_user_assigned_identity.frontendIdentity.client_id
      }
      env {
        name  = "AZ_KEYVAULT_HOST"
        value = azurerm_key_vault.keyVault.vault_uri
      }
      env {
        name  = "REDIS_HOST"
        value = azurerm_container_app.redisContainer.name
      }
      env {
        name  = "REDIS_PORT"
        value = var.redis_port
      }
      env {
        name  = "REDIS_SESSION_DB"
        value = var.redis_session_db
      }
    }
    min_replicas = terraform.workspace == "prod" ? 1 : 0
    http_scale_rule {
      name                = "http-scaler"
      concurrent_requests = "1000"
    }
    # consider adjust to "20" or more, if the apps can handle it!
  }

  ingress {
    target_port      = 3000 # change to 7071 or whatever frontend uses
    external_enabled = true
    # allow_insecure_connections = false # consider adding this
    traffic_weight {
      percentage = 100
      # TBD: remove when using single after this bug is fixed:
      # https://github.com/hashicorp/terraform-provider-azurerm/issues/20435
      latest_revision = true
    }
  }

  identity {
    type = "UserAssigned"
    identity_ids = [
      azurerm_user_assigned_identity.frontendIdentity.id,
    ]
  }


  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

resource "azurerm_container_app" "BackendAPIContainer" {
  name                         = "${var.project_short_name}-backend-${terraform.workspace}"
  container_app_environment_id = azurerm_container_app_environment.ContainerEnvironment.id
  resource_group_name          = azurerm_resource_group.resourceGroup.name

  # Never change the imaage of the container, as this is done in github actions!
  # Never overwrite the secrets set from github actions!

  # TBD: get back in, when environment variables are set azure: 
  lifecycle {
    ignore_changes = [template[0].container[0].image] # ignore secret diffs; ingress TBD when adding mounts
  }
  revision_mode = "Single"

  template {
    container {
      name   = "backend"
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
      cpu    = 0.25
      memory = "0.5Gi"
      volume_mounts {
        name = "${terraform.workspace}-application-data"
        path = "/data"
      }
      env {
        name  = "FRONTEND_SVELTE_ORIGIN"
        value = azurerm_container_app.FrontendSvelteContainer.name
      }
      env {
        name  = "FRONTEND_SVELTE_FQDN"
        value = azurerm_container_app.FrontendSvelteContainer.ingress[0].fqdn
      }
      # BackendAPI:
      // Needs client id for Pod implmentations - see here:
      // https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.managedidentitycredential?view=azure-python
      env {
        name  = "AZ_CLIENT_ID"
        value = azurerm_user_assigned_identity.backendIdentity.client_id
      }
      env {
        name  = "AZ_KEYVAULT_HOST"
        value = azurerm_key_vault.keyVault.vault_uri
      }
      # Postgres:
      env {
        name  = "POSTGRES_HOST"
        value = azurerm_postgresql_flexible_server.postgresServer.fqdn
      }
      env {
        name        = "POSTGRES_USER"
        secret_name = "postgres-user"
      }
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = "postgres-password"
      }
      env {
        name  = "POSTGRES_DB"
        value = "${terraform.workspace}_db"
      }
      # Probably not needed!
      env {
        name  = "POSTGRES_PORT"
        value = var.postgres_port
      }
      # Redis:
      env {
        name  = "REDIS_HOST"
        value = azurerm_container_app.redisContainer.name
      }
      env {
        name  = "REDIS_PORT"
        value = var.redis_port
      }
      env {
        name  = "REDIS_SESSION_DB"
        value = var.redis_session_db
      }
      env {
        name  = "REDIS_SOCKETIO_DB"
        value = var.redis_socketio_db
      }
      env {
        name  = "REDIS_CELERY_BROKER_DB"
        value = var.redis_celery_broker_db
      }
      env {
        name  = "REDIS_CELERY_BACKEND_DB"
        value = var.redis_celery_backend_db
      }
    }
    volume {
      name         = "${terraform.workspace}-application-data"
      storage_name = azurerm_container_app_environment_storage.applicationDataConnect.name
      storage_type = "AzureFile"
    }
    # leave at least 1 bakend running now in stage & prod
    min_replicas = terraform.workspace == "prod" ? 1 : 0
    max_replicas = 1 # SocketIO breaks with more than 1 replica!
    http_scale_rule {
      name                = "http-scaler"
      concurrent_requests = "1000"
    }
    # consider adjust to to less after load testing!
  }

  ingress {
    # TBD: add session_affinity = true when available
    # see here: https://github.com/Azure/terraform-azure-container-apps/issues/79
    # before scaling backend to more than max_replicas > 1
    target_port      = 80
    external_enabled = true
    # allow_insecure_connections = false # consider adding this
    traffic_weight {
      percentage = 100
      # TBD: remove when using single after this bug is fixed:
      # https://github.com/hashicorp/terraform-provider-azurerm/issues/20435
      latest_revision = true
    }
  }

  identity {
    type = "UserAssigned"
    identity_ids = [
      azurerm_user_assigned_identity.backendIdentity.id,
    ]
  }


  secret {
    name                = "postgres-password"
    identity            = azurerm_user_assigned_identity.backendIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.postgresPassword.id
    # value = data.azurerm_key_vault_secret.keyVaultSecret["postgres-password"].value
    # value = azurerm_key_vault_secret.postgresPassword.value
  }

  secret {
    name                = "postgres-user"
    identity            = azurerm_user_assigned_identity.backendIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.postgresUser.id
    # value = data.azurerm_key_vault_secret.keyVaultSecret["postgres-user"].value
    # value = azurerm_key_vault_secret.postgresUser.value
  }


  # secret {
  #   name  = "keyvault-health"
  # value = data.azurerm_key_vault_secret.keyVaultSecret["keyvault-health"].value
  # value = azurerm_key_vault_secret.keyvaultHealth.value
  # }

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

resource "azurerm_container_app" "BackendWorkerContainer" {
  name                         = "${var.project_short_name}-worker-${terraform.workspace}"
  container_app_environment_id = azurerm_container_app_environment.ContainerEnvironment.id
  resource_group_name          = azurerm_resource_group.resourceGroup.name

  # Never change the imaage of the container, as this is done in github actions!
  # Never overwrite the secrets set from github actions!

  # TBD: get back in, when environment variables are set azure: 
  lifecycle {
    ignore_changes = [template[0].container[0].image] # ingress TBD when adding mounts
  }

  revision_mode = "Single"

  template {
    container {
      name   = "worker"
      image  = "mcr.microsoft.com/azuredocs/containerapps-helloworld:latest"
      cpu    = 0.25
      memory = "0.5Gi"
      volume_mounts {
        name = "${terraform.workspace}-application-data"
        path = "/data"
      }
      # BackendWorker:
      // Needs client id for Pod implmentations - see here:
      // https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.managedidentitycredential?view=azure-python
      env {
        name  = "AZ_CLIENT_ID"
        value = azurerm_user_assigned_identity.workerIdentity.client_id
      }
      env {
        name  = "AZ_KEYVAULT_HOST"
        value = azurerm_key_vault.keyVault.vault_uri
      }
      # Postgres:
      env {
        name  = "POSTGRES_HOST"
        value = azurerm_postgresql_flexible_server.postgresServer.fqdn
      }
      env {
        name        = "POSTGRES_USER"
        secret_name = "postgres-user"
      }
      env {
        name        = "POSTGRES_PASSWORD"
        secret_name = "postgres-password"
      }
      env {
        name  = "POSTGRES_DB"
        value = "${terraform.workspace}_db"
      }
      # Probably not needed!
      env {
        name  = "POSTGRES_PORT"
        value = var.postgres_port
      }
      # Redis:
      env {
        name  = "REDIS_HOST"
        value = azurerm_container_app.redisContainer.name
      }
      env {
        name  = "REDIS_PORT"
        value = var.redis_port
      }
      env {
        name  = "REDIS_CELERY_BROKER_DB"
        value = var.redis_celery_broker_db
      }
      env {
        name  = "REDIS_CELERY_BACKEND_DB"
        value = var.redis_celery_backend_db
      }
    }
    volume {
      name         = "${terraform.workspace}-application-data"
      storage_name = azurerm_container_app_environment_storage.applicationDataConnect.name
      storage_type = "AzureFile"
    }
    # leave at least 1 bakend running now in stage & prod
    min_replicas = terraform.workspace == "prod" ? 1 : 0
    max_replicas = 10
    http_scale_rule {
      name                = "http-scaler"
      concurrent_requests = "1000"
    }
    # consider adjust to to less after load testing!
  }


  identity {
    type = "UserAssigned"
    identity_ids = [
      azurerm_user_assigned_identity.workerIdentity.id,
    ]
  }

  secret {
    name                = "postgres-password"
    identity            = azurerm_user_assigned_identity.workerIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.postgresPassword.id
    # value = "fromTerraformChangedInGithubActions"
    # value = azurerm_key_vault_secret.postgresPassword.value
    # value = data.azurerm_key_vault_secret.keyVaultSecret["postgres-password"].value
  }

  secret {
    name                = "postgres-user"
    identity            = azurerm_user_assigned_identity.workerIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.postgresUser.id
    # value = "fromTerraformChangedInGithubActions"
    # value = azurerm_key_vault_secret.postgresUser.value
    # value = data.azurerm_key_vault_secret.keyVaultSecret["postgres-user"].value
  }

  # secret {
  #   name = "postgres-host"
  #   # value = "fromTerraformChangedInGithubActions"
  #   value = azurerm_postgresql_flexible_server.postgresServer.fqdn
  # }


  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}


# DEBUGGING TCP connection to Redis on internal postgres:
# in FRONTEND container:
# - apk add tcptraceroute
# gives tcpping command
# - apk add redis
# gives redis-cli command
# also useful: wget and nslookup
# in REDIS container:
# install net-tools to get ifconfig command
# - apt install net-tools
# other useful commands: netstat


resource "azurerm_container_app" "redisContainer" {
  name                         = "${var.project_short_name}-redis-${terraform.workspace}"
  container_app_environment_id = azurerm_container_app_environment.ContainerEnvironment.id
  resource_group_name          = azurerm_resource_group.resourceGroup.name
  revision_mode                = "Single"

  identity {
    type = "UserAssigned"
    identity_ids = [
      azurerm_user_assigned_identity.redisIdentity.id,
    ]
  }

  template {
    container {
      name    = "redis"
      image   = "redis:8.2.2-alpine3.22"
      command = ["/bin/sh", "/data/entrypoint.sh"]
      cpu     = 0.25
      memory  = "0.5Gi"
      # env {
      #   name  = "REDIS_HOST"
      #   value = "${var.project_short_name}-redis-${terraform.workspace}"
      # }
      env {
        name  = "REDIS_PORT"
        value = var.redis_port
      }
      env {
        name        = "REDIS_PASSWORD"
        secret_name = "redis-password"
      }
      env {
        name        = "REDIS_SESSION_PASSWORD"
        secret_name = "redis-session-password"
      }
      env {
        name        = "REDIS_SOCKETIO_PASSWORD"
        secret_name = "redis-socketio-password"
      }
      env {
        name        = "REDIS_CELERY_PASSWORD"
        secret_name = "redis-celery-password"
      }
      # Bump config version to trigger new revision when any mounted file changes
      env {
        name = "REDIS_CONFIG_VERSION"
        value = sha256(join(",", [
          filesha256("${path.module}/../cache/entrypoint.sh"),
          filesha256("${path.module}/../cache/redis.conf"),
          filesha256("${path.module}/../cache/redis-full.conf"),
          filesha256("${path.module}/../cache/users_template.acl"),
        ]))
      }
      volume_mounts {
        name = "${terraform.workspace}-redis-data"
        path = "/data"
      }
    }
    volume {
      name         = "${terraform.workspace}-redis-data"
      storage_name = azurerm_container_app_environment_storage.redisDataConnect.name
      storage_type = "AzureFile"
    }
    # leave at least 1 min-replica for Redis - otherwise connections are lost when scaled to 0!
    min_replicas = terraform.workspace == "stage" || terraform.workspace == "prod" ? 1 : 0
    max_replicas = 1 # SocketIO breaks with more than 1 replica!
    tcp_scale_rule {
      name                = "tcp-scaler"
      concurrent_requests = "1000"
      # consider adjust to to less after load testing!
    }

  }

  ingress {
    # does not make sense: all ports are internal!
    # target_port      = terraform.workspace == "dev" || terraform.workspace == "stage" ? [ var.redis_port, var.redis_insight_port ] : [ var.redis_port ]
    target_port      = var.redis_port
    external_enabled = false # true
    # TBD: set this one back to false, once internal connections to TCP are working!
    # connection with application URI from Redis is working with this set to true.
    # external_enabled = false
    # allow_insecure_connections = false # consider adding this
    traffic_weight {
      percentage = 100
      # TBD: remove when using single after this bug is fixed:
      # https://github.com/hashicorp/terraform-provider-azurerm/issues/20435
      latest_revision = true
      # TBD: change to TCP?
      # TBD: do I need to set external_port?
      # exposed_port = var.redis_port
    }
    exposed_port = var.redis_port
    transport    = "tcp"
  }

  secret {
    name                = "redis-password"
    identity            = azurerm_user_assigned_identity.redisIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.redisPassword.id
    # value = azurerm_key_vault_secret.redisPassword.value
    # value = data.azurerm_key_vault_secret.keyVaultSecret["redis-password"].value
  }
  secret {
    name                = "redis-session-password"
    identity            = azurerm_user_assigned_identity.redisIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.redisSessionPassword.id
    # value = azurerm_key_vault_secret.redisSessionPassword.value
    # value = data.azurerm_key_vault_secret.keyVaultSecret["redis-session-password"].value
  }
  secret {
    name                = "redis-socketio-password"
    identity            = azurerm_user_assigned_identity.redisIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.redisSocketioPassword.id
    # value = azurerm_key_vault_secret.redisSocketioPassword.value
    # value = data.azurerm_key_vault_secret.keyVaultSecret["redis-socketio-password"].value
  }
  secret {
    name                = "redis-celery-password"
    identity            = azurerm_user_assigned_identity.redisIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.redisCeleryPassword.id
    # value = azurerm_key_vault_secret.redisCeleryPassword.value
    # value = data.azurerm_key_vault_secret.keyVaultSecret["redis-celery-password"].value
  }

  # TBD: check what this is needed for in the other containers!
  # needed to access keyvault!
  # identity {
  #   type = "UserAssigned"
  #   identity_ids = [
  #     azurerm_user_assigned_identity.redisIdentity.id,
  #   ]
  # }

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

# Container not starting up:
# sudo: The "no new privileges" flag is set, which prevents sudo from running as root.
# sudo: If sudo is running in a container, you may need to adjust the container configuration to disable the flag.
# TBD: configure OAuth for pgadmin container in config.py, config_local.py or config_system.py
resource "azurerm_container_app" "postgresAdmin" {
  count                        = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  name                         = "${var.project_short_name}-pgadmin-${terraform.workspace}"
  container_app_environment_id = azurerm_container_app_environment.ContainerEnvironment.id
  resource_group_name          = azurerm_resource_group.resourceGroup.name

  lifecycle {
    ignore_changes = [ingress]
  }
  revision_mode = "Single"

  template {
    container {
      name   = "pgadmin"
      image  = "dpage/pgadmin4:9.11.0"
      cpu    = 0.25
      memory = "0.5Gi"
      # volume_mounts {
      #   name = "${terraform.workspace}-admin-data"
      #   # SMB file mounts - as azure file share - conflict with linux chmod requirements of pgadmin
      #   # path = "/var/lib/pgadmin/storage"
      #   # TBD: change back to /var/lib/storage after exteranl database is in place!
      #   path = "/data"
      #   sub_path = azurerm_storage_share_directory.pgAdminDirectory[0].name
      # }
      volume_mounts {
        name     = "${terraform.workspace}-admin-data"
        path     = "/scripts"
        sub_path = azurerm_storage_share_directory.pgAdminScriptsDirectory[0].name
      }
      volume_mounts {
        name = "${terraform.workspace}-admin-data"
        # SMB file mounts - as azure file share - conflict with linux chmod requirements of pgadmin
        # so mounting and persisting data and SQLite database to /var/lib/pgadmin is not possible!
        path     = "/var/lib/pgadmin/storage"
        sub_path = azurerm_storage_share_directory.pgAdminStorageDirectory[0].name
      }
      # Silence Gunicorn webserver - otherwise all HTTP requests are printed to container app logs:
      env {
        name  = "GUNICORN_ACCESS_LOGFILE"
        value = "/dev/null"
      }
      env {
        name  = "CONSOLE_LOG_LEVEL"
        value = "10"
      }
      ################
      # TBD: comment after switching to OAuth2 login only
      # Default user name and password authentication:
      env {
        name        = "PGADMIN_DEFAULT_EMAIL"
        secret_name = "pgadmin-default-email"
      }
      env {
        name        = "PGADMIN_DEFAULT_PASSWORD"
        secret_name = "pgadmin-default-password"
      }
      ################
      # using external database - so no need for internal Sqlite db, which does not work on SMB volume mounts:
      env {
        name        = "PGADMIN_CONFIG_CONFIG_DATABASE_URI"
        secret_name = "pgadmin-database-uri"
      }
      # To fix setup error:
      env {
        name        = "PGADMIN_SETUP_EMAIL"
        secret_name = "pgadmin-default-email"
      }
      env {
        name        = "PGADMIN_SETUP_PASSWORD"
        secret_name = "pgadmin-default-password"
      }
      # TBD: update to use psycopg3 when pgadmin bug is fixed!
      # To avoid error:
      # File "/venv/lib/python3.14/site-packages/sqlalchemy/dialects/postgresql/psycopg2.py", line 696, in import_dbapi
      # import psycopg2
      # ModuleNotFoundError: No module named 'psycopg2'
      # env{
      #   name ="PGADMIN_CONFIG_PG_DEFAULT_DRIVER"
      #   value ="'psycopg2'"
      # }
      # Preconfigure database servers inside pgadmin - works only with internal login, not with OAuth2:
      # env {
      #   name  = "PGADMIN_SERVER_JSON_FILE"
      #   value = "/data/pgadmin/servers.json"
      # }
      # Configure authentication for pgadmin:
      # This one is fed through the hook script - not a direct variable for PGADMIN:
      env {
        name        = "PGADMIN_MASTER_PASSWORD"
        secret_name = "pgadmin-master-password"
      }
      env {
        name  = "PGADMIN_CONFIG_MASTER_PASSWORD_HOOK"
        value = "'/scripts/set_master_password.sh'"
        # value = "'/data/set_master_password.sh'"
        # value = "'/var/lib/pgadmin/storage/set_master_password.sh'"
      }
      env {
        name = "PGADMIN_CONFIG_AUTHENTICATION_SOURCES"
        # For initial configuration use both "internal" and "oauth2"!
        # value = "['oauth2', 'internal']"
        value = "['oauth2']"
      }
      env {
        name  = "PGADMIN_CONFIG_OAUTH2_AUTO_CREATE_USER"
        value = "True"
      }
      env {
        name  = "PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED"
        value = "True"
      }
      # Configure OAuth with Azure AD:
      env {
        name        = "PGADMIN_CONFIG_OAUTH2_CONFIG"
        secret_name = "pgadmin-oauth2-config"
      }
    }
    volume {
      name         = "${terraform.workspace}-admin-data"
      storage_name = azurerm_container_app_environment_storage.adminDataConnect[0].name
      storage_type = "AzureFile"
      # mount_options = "uid=5050,gid=5050,dir_mode=0700,file_mode=0700" # pgadmin user
    }
    min_replicas = 0
    max_replicas = 1
  }

  ingress {
    target_port      = 80
    external_enabled = true
    # allow_insecure_connections = false # consider adding this
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  identity {
    type = "UserAssigned"
    identity_ids = [
      azurerm_user_assigned_identity.pgadminIdentity.id,
    ]
  }

  ################
  # TBD: comment after switching to OAuth2 login only
  secret {
    name                = "pgadmin-default-email"
    identity            = azurerm_user_assigned_identity.pgadminIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.pgadminDefaultEmail[0].id
  }

  secret {
    name                = "pgadmin-default-password"
    identity            = azurerm_user_assigned_identity.pgadminIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.pgadminDefaultPassword[0].id
  }
  ################
  secret {
    name                = "pgadmin-database-uri"
    identity            = azurerm_user_assigned_identity.pgadminIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.pgadminDatabaseURI[0].id
  }
  secret {
    name                = "pgadmin-master-password"
    identity            = azurerm_user_assigned_identity.pgadminIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.pgadminMasterPassword[0].id
  }

  secret {
    name                = "pgadmin-oauth2-config"
    identity            = azurerm_user_assigned_identity.pgadminIdentity.id
    key_vault_secret_id = azurerm_key_vault_secret.pgadminOauth2Config[0].id
  }

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

# resource "azurerm_container_app" "postgresContainer" {
#   name                         = "${var.project_short_name}-postgres-${terraform.workspace}"
#   container_app_environment_id = azurerm_container_app_environment.ContainerEnvironment.id
#   resource_group_name          = azurerm_resource_group.resourceGroup.name
#   revision_mode = "Single"

#   template {
#     container {
#       name   = "postgres"
#       image  = "postgres:18.0-alpine3.22"
#       cpu    = 0.25
#       memory = "0.5Gi"
#       volume_mounts {
#         name = "${terraform.workspace}-postgres-data"
#         path = "/var/lib/postgresql/data"
#       }
#     }
#     volume {
#       name         = "${terraform.workspace}-postgres-data"
#       storage_name = azurerm_container_app_environment_storage.postgresDataConnect.name
#       storage_type = "AzureFile"
#     }
#     # Keep awake in stage and production:
#     min_replicas = terraform.workspace == "stage" || terraform.workspace == "prod" ? 1 : 0
#     max_replicas = 1
#   }

#   # TBD: add ingress when needed!
#   # ingress {}

#   # # TBD: check what this is needed for in the other containers!
#   # # needed to access keyvault!
#   # identity {
#   #   type = "UserAssigned"
#   #   identity_ids = [
#   #     azurerm_user_assigned_identity.postgresIdentity.id,
#   #   ]
#   # }

#   tags = {
#     Costcenter  = var.costcenter
#     Owner       = var.owner_name
#     Environment = terraform.workspace
#   }
# }
