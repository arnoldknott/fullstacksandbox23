#!/bin/bash

# USE: ./scripts/deploy_infrastructure.sh

# This script is used to deploy the infrastructure from localhost using an OpenTofu container.

# Documentation on how to register the service principle for the GitHub environment "infrastructure":
# https://registry.terraform.io/providers/hashicorp/azuread/latest/docs/guides/service_principal_configuration
# It requires authentication to Azure via a service principle.
# Create the service principle via Azure CLI:
# az ad sp create-for-rbac --name "<name-of-service-principle>" --role="Contributor" --scopes="/subscriptions/<subscription-id>"
# (Note: it needs access to the whole subscription, so the infrastructure can be create in resource groups)
# Also needs "Storage Blob Data Contributor" role assignment to the service principle:
# https://stackoverflow.com/questions/52769758/azure-blob-storage-authorization-permission-mismatch-error-for-get-request-wit
# https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-access-azure-active-directory
# az role assignment create \
#   --role "Contributor" \
#   --assignee <object_id_of_app> \
#   --scope /subscriptions/<subscription_id>
# az role assignment create \
#   --role "Storage Blob Data Contributor"
#   --assignee <object_id_of_app>
#   --scope /subscriptions/<subscription_id>/resourceGroups/<resource_group_name>/providers/Microsoft.Storage/storageAccounts/<storage_account_name>/blobServices/default/containers/<container_name>
# * object_id_of_app is not the allplication id.
# az role assignment create \
#   --role "User Access Administrator" \
#   --assignee <object_id_of_app> \
#   --scope /subscriptions/<subscription_id>/resourceGroups/<resource_group_name>

# create the workspaces manually:
# ./scripts/start_infrastructure.sh # to get into the container
# cp -fR .azure/ ~/.azure
# tofu init \
#         -backend-config="resource_group_name=${AZ_RESOURCE_GROUP_NAME}" \
#         -backend-config="storage_account_name=${AZ_STORAGE_ACCOUNT_NAME}" \
#         -backend-config="container_name=${AZ_CONTAINER_NAME}" \
#         -backend-config="key=${AZ_BACKEND_STATE_KEY}" \
#         -var "azure_tenant_id=${AZURE_TENANT_ID}" \
#         -var "azure_client_id=${AZURE_CLIENT_ID}" \
#         -var "azure_subscription_id=${AZURE_SUBSCRIPTION_ID}"
# tofu workspace new dev
# tofu workspace new stage
# tofu workspace new prod
# tofu init \
#         -backend-config="resource_group_name=${AZ_RESOURCE_GROUP_NAME}" \
#         -backend-config="storage_account_name=${AZ_STORAGE_ACCOUNT_NAME}" \
#         -backend-config="container_name=${AZ_CONTAINER_NAME}" \
#         -backend-config="key=${AZ_BACKEND_STATE_KEY}" \
#         -var "azure_tenant_id=${AZURE_TENANT_ID}" \
#         -var "azure_client_id=${AZURE_CLIENT_ID}" \
#         -var "azure_subscription_id=${AZURE_SUBSCRIPTION_ID}" \
#         -reconfigure

echo "=== Running: deploy_infrastructure ==="

echo ""
echo "=== initialize the script ==="
# Initialization:
REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
BRANCH_NAME=$(git branch --show-current)
cd $REPO_ROOT_DIR/infrastructure

echo ""
echo "=== set workspace ==="
if [ "$BRANCH_NAME" == "dev" ]; then
    WORKSPACE=dev
elif [ "$BRANCH_NAME" == "stage" ]; then
    WORKSPACE=stage
elif [ "$BRANCH_NAME" == "main" ]; then
    WORKSPACE=prod
else
    echo "Branch name not recognized"
    exit 1
fi
echo "==> workspace is set to: $WORKSPACE <=="

echo ""
echo "=== get public ssh keys from localhost ==="
local_public_ssh_key_path=$(eval echo $(grep SSH_KEY_PATH_LOCALHOST .env | cut -d '=' -f 2 | tr -d ' "'))
public_ssh_key_path=$(eval echo $(grep PUBLIC_SSH_KEY_PATH .env | cut -d '=' -f 2 | tr -d ' "'))
# echo "local_public_ssh_key_path: $local_public_ssh_key_path"
# echo "public_ssh_key_path: $public_ssh_key_path"
cp $local_public_ssh_key_path $public_ssh_key_path


echo ""
echo "=== use Azure login information from host in container ==="
{
    # try
    az account show --output none
} ||
{
    # catch
    az login --tenant $(grep AZURE_TENANT_ID .env | cut -d '=' -f 2 | tr -d ' "')
    
}
az account set --subscription $(grep AZURE_SUBSCRIPTION_ID .env | cut -d '=' -f 2 | tr -d ' "')
mkdir -p .azure
az account get-access-token --resource https://management.azure.com/ --output json > .azure/azure_token.json
cp -fR ~/.azure/* .azure/

echo ""
echo "=== building the tofu container ==="
docker compose build


### This part with docker compose up ###
# echo "=== starting the tofu container ==="
# docker compose up -d t--remove-orphans ofu

# echo "=== tofu - version ==="
# docker compose exec tofu tofu --version

# echo "=== monitoring variables ==="
# docker compose exec tofu echo $AZ_STORAGE_ACCOUNT_NAME
# docker compose exec -e "WORKSPACE=${WORKSPACE}" tofu echo $WORKSPACE
#################

# This worked without entrypoint in docker compose file  -until tofu workspace select:
echo ""
echo "=== tofu - version ==="
docker compose run --rm tofu --version
# docker compose exec tofu tofu --version
# docker compose exec tofu tofu --version

# echo ""
# echo "=== monitoring variables ==="
# # docker compose exec --entrypoint "echo $AZ_STORAGE_ACCOUNT_NAME" tofu 
# # docker compose exec tofu echo $ARM_CLIENT_ID
# docker compose run --rm --entrypoint '/bin/bash -c' tofu 'echo ${AZ_STORAGE_ACCOUNT_NAME}'
# docker compose run --rm --entrypoint '/bin/bash -c' tofu 'echo ${POSTGRES_PORT}'
# docker compose run --rm -e "WORKSPACE=${WORKSPACE}"  --entrypoint '/bin/bash -c' tofu 'echo ${WORKSPACE}'
# # docker compose run --rm --entrypoint "pwd" tofu 
# docker compose run --rm -e "WORKSPACE=${WORKSPACE}" --entrypoint '/bin/sh -c' tofu 'ls -la'

echo ""
echo "=== tofu - init ==="
docker compose run --rm --entrypoint '/bin/sh -c' tofu 'cp -fR .azure/ ~/.azure &&
tofu init \
        -backend-config="resource_group_name=${AZ_RESOURCE_GROUP_NAME}" \
        -backend-config="storage_account_name=${AZ_STORAGE_ACCOUNT_NAME}" \
        -backend-config="container_name=${AZ_CONTAINER_NAME}" \
        -backend-config="key=${AZ_BACKEND_STATE_KEY}" \
        -var "azure_tenant_id=${AZURE_TENANT_ID}" \
        -var "azure_client_id=${AZURE_CLIENT_ID}" \
        -var "azure_subscription_id=${AZURE_SUBSCRIPTION_ID}"'

echo ""
echo "=== tofu - workspace select ==="
# docker compose run --rm -e "WORKSPACE=${WORKSPACE}" tofu workspace select -or-create ${WORKSPACE}
# docker compose run --rm -e "WORKSPACE=${WORKSPACE}" tofu workspace select -or-create \
#         -var "azure_tenant_id=${AZURE_TENANT_ID}" \
#         -var "azure_client_id=${AZURE_CLIENT_ID}" \
#         -var "azure_subscription_id=${AZURE_SUBSCRIPTION_ID}" \
#         ${WORKSPACE}
docker compose run --rm -e "WORKSPACE=${WORKSPACE}" --entrypoint '/bin/sh -c' tofu 'cp -fR .azure/ ~/.azure &&
tofu workspace select -or-create \
        -var "azure_tenant_id=${AZURE_TENANT_ID}" \
        -var "azure_client_id=${AZURE_CLIENT_ID}" \
        -var "azure_subscription_id=${AZURE_SUBSCRIPTION_ID}" \
        ${WORKSPACE}'
echo "selected workspace:"
docker compose run --rm tofu workspace show

echo ""
echo "=== tofu - plan ==="
set +e
# docker compose run --rm -e "WORKSPACE=${WORKSPACE}" tofu plan -out=${WORKSPACE}.tfplan \
# docker compose cp ./ssh_key.pub tofu:$local_public_ssh_key_path
docker compose run --rm -e "WORKSPACE=${WORKSPACE}" --entrypoint '/bin/sh -c' tofu 'cp -fR .azure/ ~/.azure &&
ARM_CLIENT_SECRET=$AZURE_CLIENT_SECRET &&
tofu plan -out=${WORKSPACE}.tfplan \
        -detailed-exitcode \
        -var "azure_tenant_id=${AZURE_TENANT_ID}" \
        -var "azure_client_id=${AZURE_CLIENT_ID}" \
        -var "azure_subscription_id=${AZURE_SUBSCRIPTION_ID}" \
        -var "old_repo_service_principle_object_id=${OLD_REPO_SERVICE_PRINCIPLE_OBJECT_ID}" \
        -var "developer_localhost_object_id=${DEVELOPER_LOCALHOST_OBJECT_ID}" \
        -var "managed_identity_github_actions_object_id=${MANAGED_IDENTITY_GITHUB_ACTIONS_OBJECT_ID}" \
        -var "project_name=${PROJECT_NAME}" \
        -var "project_short_name=${PROJECT_SHORT_NAME}" \
        -var "project_repository_name=${PROJECT_REPOSITORY_NAME}" \
        -var "costcenter=${COSTCENTER}" \
        -var "owner_name=${OWNER_NAME}" \
        -var "budget_notification_email=${BUDGET_NOTIFICATION_EMAIL}" \
        -var "owner_object_id=${OWNER_OBJECT_ID}" \
        -var "postgres_port=${POSTGRES_PORT}" \
        -var "redis_port=${REDIS_PORT}" \
        -var "redis_insight_port=${REDIS_INSIGHT_PORT}" \
        -var "redis_session_db=${REDIS_SESSION_DB}" \
        -var "public_ssh_key_path=${PUBLIC_SSH_KEY_PATH}"'

# Comes from ARM_ environment variable, as it is not needed with managed identity in the Github Actions workflow:
# -var "azure_client_secret=${AZURE_CLIENT_SECRET}" \
#
# -var "azure_tenant_id=${ARM_TENANT_ID}" \
# trying with user login instead of service principle inside container:
# tofu plan -out=${WORKSPACE}.tfplan \
#         -detailed-exitcode \
#         -var "azure_tenant_id=${azure_tenant_id}" \
#         -var "azure_client_id=${azure_client_id}" \
#         -var "azure_client_secret=${azure_client_secret}" \
#         -var "azure_subscription_id=${azure_subscription_id}" \
#         -var "old_repo_service_principle_object_id=${OLD_REPO_SERVICE_PRINCIPLE_OBJECT_ID}" \
#         -var "developer_localhost_object_id=${DEVELOPER_LOCALHOST_OBJECT_ID}" \
#         -var "managed_identity_github_actions_object_id=${MANAGED_IDENTITY_GITHUB_ACTIONS_OBJECT_ID}" \
#         -var "project_name=${PROJECT_NAME}" \
#         -var "project_short_name=${PROJECT_SHORT_NAME}" \
#         -var "costcenter=${COSTCENTER}" \
#         -var "owner_name=${OWNER_NAME}" \
#         -var "budget_notification_email=${BUDGET_NOTIFICATION_EMAIL}" \
#         -var "owner_object_id=${OWNER_OBJECT_ID}" \
#         -var "postgres_port=${POSTGRES_PORT}" \
#         -var "redis_port=${REDIS_PORT}" \
#         -var "redis_insight_port=${REDIS_INSIGHT_PORT}" \
#         -var "redis_session_db=${REDIS_SESSION_DB}" \
#         -var "public_ssh_key_path=${PUBLIC_SSH_KEY_PATH}"
# -var "owner_user_principal_name=${OWNER_USER_PRINCIPAL_NAME}" \
# -var "azure_sp_object_id=${ARM_OBJECT_ID}" \
tofu_plan_exit_code=$?
set -e
echo "tofu_plan_exit_code: $tofu_plan_exit_code"
if [ $tofu_plan_exit_code == 1 ]; then
    echo "=== tofu - plan failed ==="
    tofu_changes_applied=1
elif [ $tofu_plan_exit_code == 0 ]; then
    echo "=== tofu - no changes ==="
    tofu_changes_applied=0
elif [ $tofu_plan_exit_code == 2 ]; then
    echo "=== tofu plan has changes ==="
    echo ""
    echo "=== tofu - approval before apply ==="
    read -p "Apply changes? (Y/N): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        echo "=== tofu - apply ==="
        # docker compose run --rm -e "WORKSPACE=${WORKSPACE}" tofu apply -auto-approve ${WORKSPACE}.tfplan
        docker compose run --rm -e "WORKSPACE=${WORKSPACE}" --entrypoint '/bin/sh -c' tofu 'cp -fR .azure/ ~/.azure &&
        ARM_CLIENT_SECRET=$AZURE_CLIENT_SECRET &&
        tofu apply -auto-approve ${WORKSPACE}.tfplan'
        # tofu apply -auto-approve \
        #     -var "azure_tenant_id=${AZURE_TENANT_ID}" \
        #     -var "azure_client_id=${AZURE_CLIENT_ID}" \
        #     -var "azure_subscription_id=${AZURE_SUBSCRIPTION_ID}" \
        #     ${WORKSPACE}.tfplan'
        tofu_changes_applied=0
    else
        echo "=== tofu - apply not confirmed ==="
        tofu_changes_applied=1
    fi
    # read -p "Apply changes? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    # echo "=== tofu - apply ==="
    # # docker compose run --rm -e "WORKSPACE=${WORKSPACE}" tofu apply -auto-approve ${WORKSPACE}.tfplan
    # docker compose run --rm -e "WORKSPACE=${WORKSPACE}" --entrypoint '/bin/sh -c' tofu 'cp -fR .azure/ ~/.azure &&
    # ARM_CLIENT_SECRET=$AZURE_CLIENT_SECRET &&
    # tofu apply -auto-approve \
    #         -var "azure_tenant_id=${AZURE_TENANT_ID}" \
    #         -var "azure_client_id=${AZURE_CLIENT_ID}" \
    #         -var "azure_subscription_id=${AZURE_SUBSCRIPTION_ID}" \
    #         ${WORKSPACE}.tfplan'
else
    echo "=== tofu plan failed with unknown output ==="
    tofu_changes_applied=1
fi

echo ""
echo "=== remove the public ssh from working directory ==="
rm -f $public_ssh_key_path

echo ""
echo "=== remove the azure login information ==="
rm -rfd .azure/*

echo ""
echo "=== tofu - finished ==="

exit $tofu_changes_applied

#### WORKS - start: ####
# echo "=== tofu - init, workspace, plan, and apply ==="
# docker compose run --rm -e "WORKSPACE=${WORKSPACE}" --entrypoint '/bin/sh -c' tofu \
#     '
#     echo "=== tofu - init ===" &&
#     tofu init \
#         -backend-config="resource_group_name=${AZ_RESOURCE_GROUP_NAME}" \
#         -backend-config="storage_account_name=${AZ_STORAGE_ACCOUNT_NAME}" \
#         -backend-config="container_name=${AZ_CONTAINER_NAME}" \
#         -backend-config="key=${AZ_BACKEND_STATE_KEY}" &&
#     echo "=== tofu - worksapce select ===" &&
#     tofu workspace select -or-create ${WORKSPACE} &&
#     echo "=== tofu - plan ===" &&
#     tofu plan -out=${WORKSPACE}.tfplan \
#         -var "project_name=${PROJECT_NAME}" \
#         -var "project_short_name=${PROJECT_SHORT_NAME}" \
#         -var "costcenter=${COSTCENTER}" \
#         -var "owner_name=${OWNER_NAME}" \
#         -var "budget_notification_email=${BUDGET_NOTIFICATION_EMAIL}" \
#         -var "owner_user_principal_name=${OWNER_USER_PRINCIPAL_NAME}" \
#         -var "postgres_port=${POSTGRES_PORT}" \
#         -var "redis_port=${REDIS_PORT}" \
#         -var "redis_insight_port=${REDIS_INSIGHT_PORT}" \
#         -var "redis_session_db=${REDIS_SESSION_DB}" \
#         -var "public_ssh_key_path=${PUBLIC_SSH_KEY_PATH}" &&
#     echo "=== tofu - approval before apply ===" &&
#     read -p "Apply changes? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1 &&
#     echo "=== tofu - apply ===" &&
#     tofu apply -auto-approve ${WORKSPACE}.tfplan
#     '
    # set +e &&
    # tofu plan -out=${WORKSPACE}.tfplan \
    #     -detailed-exitcode \
    #     -var "project_name=${PROJECT_NAME}" \
    #     -var "project_short_name=${PROJECT_SHORT_NAME}" \
    #     -var "costcenter=${COSTCENTER}" \
    #     -var "owner_name=${OWNER_NAME}" \
    #     -var "budget_notification_email=${BUDGET_NOTIFICATION_EMAIL}" \
    #     -var "owner_user_principal_name=${OWNER_USER_PRINCIPAL_NAME}" \
    #     -var "postgres_port=${POSTGRES_PORT}" \
    #     -var "redis_port=${REDIS_PORT}" \
    #     -var "redis_insight_port=${REDIS_INSIGHT_PORT}" \
    #     -var "redis_session_db=${REDIS_SESSION_DB}" \
    #     -var "public_ssh_key_path=${PUBLIC_SSH_KEY_PATH}" &&
    # tofu_plan_exit_code=$? &&
    # set -e &&
    # echo "tofu_plan_exit_code: $tofu_plan_exit_code" &&
    # if [ $tofu_plan_exit_code == 1 ]; then
    #     echo "=== tofu - plan failed ===" &&
    #     exit 1
    # elif [ $tofu_plan_exit_code == 0 ]; then
    #     echo "=== tofu - no changes ===" &&
    #     exit 0
    # elif [ $tofu_plan_exit_code == 2 ]; then
    #     echo "=== tofu plan has changes ===" &&
    #     echo "=== tofu - approval before apply ===" &&
    #     read -p "Apply changes? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1 &&
    #     echo "=== tofu - apply ===" &&
    #     tofu apply -auto-approve ${WORKSPACE}.tfplan
    # fi
    # '
#### WORKS - end ####


# add all variables to tofu plan!
# with passing the variables:
# tofu plan -out=${WORKSPACE}.tfplan \
#     -var "azure_client_id=${ARM_CLIENT_ID}" \
#     -var "azure_client_secret=${ARM_CLIENT_SECRET}" \
#     -var "azure_subscription_id=${ARM_SUBSCRIPTION_ID}" \
#     -var "azure_tenant_id=${ARM_TENANT_ID}" &&





# rm -rf .terraform



# echo "=== tofu - workspace select ${WORKSPACE} ==="
# docker compose run --rm -e "WORKSPACE=${WORKSPACE}" --entrypoint '/bin/sh -c' tofu 'tofu workspace select ${WORKSPACE}'



# old versions of the init command:
# docker compose run --rm -e "WORKSPACE=${WORKSPACE}" --entrypoint '/bin/sh -c' tofu 'tofu init \
#     -backend-config="resource_group_name=${AZ_RESOURCE_GROUP_NAME}" \
#     -backend-config="storage_account_name=${AZ_STORAGE_ACCOUNT_NAME}" \
#     -backend-config="container_name=${AZ_CONTAINER_PREFIX}-${WORKSPACE}" \
#     -backend-config="key=${AZ_BACKEND_STATE_KEY}"'
# docker compose exec tofu tofu init
# docker compose run --rm tofu init \
#     -backend-config="resource_group_name=$AZ_RESOURCE_GROUP_NAME" \
#     -backend-config="storage_account_name=$AZ_STORAGE_ACCOUNT_NAME" \
#     -backend-config="container_name=$AZ_CONTAINER_NAME" \
#     -backend-config="key=$AZ_BACKEND_STATE_KEY"
# docker compose run --rm tofu init \
#     -backend-config='resource_group_name=${AZ_RESOURCE_GROUP_NAME}' \
#     -backend-config='storage_account_name=${AZ_STORAGE_ACCOUNT_NAME}' \
#     -backend-config='container_name=${AZ_CONTAINER_PREFIX}-dev' \
#     -backend-config='key=${AZ_BACKEND_STATE_KEY}'
# docker compose exec tofu tofu init \
#     --backend-config="resource_group_name=${AZ_RESOURCE_GROUP_NAME}" \
#     --backend-config="storage_account_name=${AZ_STORAGE_ACCOUNT_NAME}" \
#     --backend-config="container_name=${AZ_CONTAINER_PREFIX}-\${terraform.workspace}" \
#     --backend-config="key=${AZ_BACKEND_STATE_KEY}"
# docker compose run --rm tofu init \
#     --backend-config="resource_group_name=${AZ_RESOURCE_GROUP_NAME}" \
#     --backend-config="storage_account_name=${AZ_STORAGE_ACCOUNT_NAME}" \
#     --backend-config="container_name=${AZ_CONTAINER_PREFIX}-\${terraform.workspace}" \
#     --backend-config="key=${AZ_BACKEND_STATE_KEY}"

# only required for plan & apply ?:
    # -var "azure_client_id=${ARM_CLIENT_ID}" \
    # -var "azure_client_secret=${ARM_CLIENT_SECRET}" \
    # -var "azure_tenant_id=${ARM_TENANT_ID}" \
    # -var "subscription_id=${ARM_SUBSCRIPTION_ID}" \

# echo "=== tofu - workspace select ${WORKSPACE} ==="
# docker compose run --rm tofu workspace select ${WORKSPACE}

# -var-file="terraform.tfvars"

# docker compose down --remove-orphans