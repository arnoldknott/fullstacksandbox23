# # TBD: remove - should not be needed any more?
# resource "azuread_application" "GithubActions" {
#   display_name            = "${var.project_name}-githubActions-${terraform.workspace}"
#   owners                  = [data.azuread_client_config.current.object_id, var.owner_object_id]
#   prevent_duplicate_names = true

#   tags = [var.costcenter, var.owner_name, terraform.workspace]
# }

# # Do I still need this?
# # TBD: remove - should not be needed any more?
# ################# Implementation through Service Principle #################
# resource "azuread_service_principal" "GithubActionsServicePrincipal" {
#   client_id    = azuread_application.GithubActions.client_id
#   description  = "Service principal that Github Actions uses to deploy the ${var.project_name} in ${terraform.workspace} environment"
#   use_existing = true
#   owners       = [data.azuread_client_config.current.object_id, var.owner_object_id]
#   tags         = [var.costcenter, var.owner_name, terraform.workspace]
# }

# # Needs Owner or User Access Administrator role to be able to assign roles to the service principal
# resource "azurerm_role_assignment" "AssigningServicePrincipalAsFrontendContributor" {
#   description          = "Allow Github Actions to update the frontend container app in ${var.project_name} in ${terraform.workspace} environment"
#   scope                = azurerm_container_app.FrontendContainer.id
#   role_definition_name = "Contributor"
#   principal_id         = azuread_service_principal.GithubActionsServicePrincipal.object_id
# }

# # Needs Owner or User Access Administrator role to be able to assign roles to the service principal
# resource "azurerm_role_assignment" "AssigningServicePrincipalAsBackendContributor" {
#   description          = "Allow Github Actions to update the backend container app in ${var.project_name} in ${terraform.workspace} environment"
#   scope                = azurerm_container_app.BackendContainer.id
#   role_definition_name = "Contributor"
#   principal_id         = azuread_service_principal.GithubActionsServicePrincipal.object_id
# }

################# Implementation through Managed Identity #################
resource "azurerm_user_assigned_identity" "GithubActionsManagedIdentity" {
  name                = "${var.project_name}-githubActionsManagedIdentity-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

# TBD: check if really necessary?
resource "azurerm_role_assignment" "github_runner" {
  scope                = azurerm_storage_account.storage.id
  role_definition_name = "Storage File Data SMB Share Contributor"
  principal_id         = azurerm_user_assigned_identity.GithubActionsManagedIdentity.principal_id
}

# Manual configurations:
# https://github.com/Azure/login
# https://learn.microsoft.com/da-dk/entra/identity/managed-identities-azure-resources/how-manage-user-assigned-managed-identities?pivots=identity-mi-methods-azp#create-a-user-assigned-managed-identity
# => find managed identity => Azure role assignment => add => resource group => Contributor
# https://learn.microsoft.com/da-dk/entra/workload-id/workload-identity-federation-create-trust-user-assigned-managed-identity?pivots=identity-wif-mi-methods-azp#github-actions-deploying-azure-resources
# => find managed identity => add federated credentials => repo settings => environment (dev, stage or prod) => Credential name: ${var.project_name}-githubActionsManagedIdentity-${terraform.workspace}
# in Github: add environment stage/prod with secrets for the managed identity: client_id, subscription_id, and tenant_id - NOTE: No secret needed!

# # Giving up on this one - and doing it manually in the portal instead!
# resource "azurerm_role_assignment" "AssigningManagedIdentityAsResourceGroupContributor" {
#   description          = "Allow Github Actions to contribute to ${azurerm_resource_group.resourceGroup.name} in ${var.project_name} in ${terraform.workspace} environment"
#   scope                = azurerm_resource_group.resourceGroup.id
#   role_definition_name = "Contributor"
#   principal_id         = azurerm_user_assigned_identity.GithubActionsManagedIdentity.principal_id
# }

# # doesn't work in container level - but works in portal on resource group level.
# resource "azurerm_role_assignment" "AssigningManagedIdentityAsFrontendContributor" {
#   description          = "Allow Github Actions to update the frontend container app in ${var.project_name} in ${terraform.workspace} environment"
#   scope                = azurerm_container_app.FrontendContainer.id
#   role_definition_name = "Contributor"
#   principal_id         = azurerm_user_assigned_identity.GithubActionsManagedIdentity.principal_id
# }

# resource "azurerm_role_assignment" "AssigningManagedIdentityAsBackendContributor" {
#   description          = "Allow Github Actions to update the backend container app in ${var.project_name} in ${terraform.workspace} environment"
#   scope                = azurerm_container_app.BackendContainer.id
#   role_definition_name = "Contributor"
#   principal_id         = azurerm_user_assigned_identity.GithubActionsManagedIdentity.principal_id
# }