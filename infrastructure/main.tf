terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.3.0"
    }
  }

  # Create manually before running the init command the first time - reuse any of the existing storage accounts. Beware of who has access to the storage account!
  # az group create --name <resource_group_name> --location <location>
  # az storage account create --name <storage_account_name> --resource-group <resource_group_name> --location <location> --sku Standard_LRS --public-network-access enabled
  # az storage container create --name <container_name> --account-name <storage_account_name># consider adding --default-encryption-scope <scope> --prevent-encryption-scope-override true
  backend "azurerm" {
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
  # client_id       = var.azure_client_id # ARM_CLIENT_ID
  # client_secret   = var.azure_client_secret # ARM_CLIENT_SECRET - not necessary, when using managed identity
  # subscription_id = var.azure_subscription_id # ARM_SUBSCRIPTION_ID
  # tenant_id       = var.azure_tenant_id # ARM_TENANT_ID
  # use_msi         = true
}

# provider "azurerm" {

#   client_id       = var.azure_client_id
#   client_secret   = var.azure_client_secret
#   subscription_id = var.azure_subscription_id
#   tenant_id       = var.azure_tenant_id

#   features {}

# }
