terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.3.0"
    }
    # azuread = {
    #   source  = "hashicorp/azuread"
    #   version = "3.0.2"
    # }
  }

  # Create manually before running the init command the first time - reuse any of the existing storage accounts. Beware of who has access to the storage account!
  # az group create --name <resource_group_name> --location <location>
  # az storage account create --name <storage_account_name> --resource-group <resource_group_name> --location <location> --sku Standard_LRS --public-network-access enabled
  # az storage container create --name <container_name> --account-name <storage_account_name># consider adding --default-encryption-scope <scope> --prevent-encryption-scope-override true
  backend "azurerm" {
    # These values are set via the argument -backend-config as key=value pairs
    #   resource_group_name  = "StorageAccount-ResourceGroup"          # Can be passed via `-backend-config=`"resource_group_name=<resource group name>"` in the `init` command.
    #   storage_account_name = "abcd1234"                              # Can be passed via `-backend-config=`"storage_account_name=<storage account name>"` in the `init` command.
    #   container_name       = "tfstate"                               # Can be passed via `-backend-config=`"container_name=<container name>"` in the `init` command.
    #   key                  = "dev.terraform.tfstate"                # Can be passed via `-backend-config=`"key=<blob key name>"` in the `init` command.
    # pass via environment variables for running local: ARM_CLIENT_ID, ARM_CLIENT_SECRET, ARM_SUBSCRIPTION_ID, ARM_TENANT_ID
    #   use_oidc             = true                                    # Can also be set via `ARM_USE_OIDC` environment variable.
    #   client_id            = "00000000-0000-0000-0000-000000000000"  # Can also be set via `ARM_CLIENT_ID` environment variable.
    #   client_secret        = "************************************"  # Can also be set via `ARM_CLIENT_SECRET` environment variable.
    #   subscription_id      = "00000000-0000-0000-0000-000000000000"  # Can also be set via `ARM_SUBSCRIPTION_ID` environment variable.
    #   tenant_id            = "00000000-0000-0000-0000-000000000000"  # Can also be set via `ARM_TENANT_ID` environment variable.
    #   use_azuread_auth     = true                                    # Can also be set via `ARM_USE_AZUREAD` environment variable.
  }
}

provider "azurerm" {
  features {}

  # Those variables should be comming from the environment variables ARM_*
  client_id = var.azure_client_id # ARM_CLIENT_ID
  # client_secret   = var.azure_client_secret # ARM_CLIENT_SECRET - not necessary, when using managed identity, but needed, when using service principle!
  dynamic "client_secret_block" {
    for_each = var.azure_client_secret != "" ? [1] : []
    content {
      client_secret = var.client_secret
    }
  }
  subscription_id = var.azure_subscription_id # ARM_SUBSCRIPTION_ID
  tenant_id       = var.azure_tenant_id       # ARM_TENANT_ID
  # use_msi         = true
}

# now deleted state-file in backend
# provider "azuread" {}

# The client registration running this terraform script
# data "azuread_client_config" "current" {}

# # The Developer / Intended owner of the app registrations
# instead of using the user principal name, we could use the object id of the user directly
# requires less priviliges for the service principle / managed identity running the infrastructure script!
# data "azuread_user" "owner" {
#   user_principal_name = var.owner_user_principal_name
# }

resource "azurerm_resource_group" "resourceGroup" {
  name = "${var.project_name}-${terraform.workspace}"
  # name = "testing-infrastructure-fssb23-${terraform.workspace}"
  location = "North Europe"
  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

### This is done manually:
# az role assignment create \
#   --role "User Access Administrator"
#   --assignee <object_id_of_app*>
#   --scope /subscriptions/<subscription_id>/resourceGroups/<resource_group_name>
# resource "azurerm_role_assignment" "tofuServicePrincipleResourceGroupOwner" {
#   scope                = azurerm_resource_group.resourceGroup.id
#   role_definition_name = "User Access Administrator"# or "Owner"
#   principal_id         = var.azure_sp_object_id
# }


resource "azurerm_monitor_action_group" "actionGroup" {
  name                = "${var.project_name}-actionGroup-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  short_name          = "SLPaction"
}

resource "azurerm_consumption_budget_resource_group" "budget" {
  name              = "${var.project_name}-${terraform.workspace}"
  resource_group_id = azurerm_resource_group.resourceGroup.id

  amount     = 100
  time_grain = "Monthly"

  time_period {
    start_date = "2023-11-01T00:00:00Z"
    end_date   = "2043-11-30T00:00:00Z"
  }

  filter {
    dimension {
      name = "ResourceId"
      values = [
        azurerm_monitor_action_group.actionGroup.id,
      ]
    }
  }

  notification {
    enabled        = true
    threshold      = 80.0
    operator       = "EqualTo"
    threshold_type = "Forecasted"

    contact_emails = [
      var.budget_notification_email,
    ]

    contact_groups = [
      azurerm_monitor_action_group.actionGroup.id,
    ]

    contact_roles = [
      "Owner",
    ]
  }

  notification {
    enabled        = true
    threshold      = 100.0
    operator       = "EqualTo"
    threshold_type = "Forecasted"

    contact_emails = [
      var.budget_notification_email,
    ]

    contact_groups = [
      azurerm_monitor_action_group.actionGroup.id,
    ]

    contact_roles = [
      "Owner",
    ]
  }
}

resource "azurerm_service_plan" "servicePlan" {
  name                = "${var.project_name}-servicePlan-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location
  os_type             = "Linux"
  sku_name            = "Y1"

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}