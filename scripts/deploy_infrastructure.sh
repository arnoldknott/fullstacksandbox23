#!/bin/bash

# USE: ./scripts/deploy_infrastructure.sh

# This script is used to deploy the infrastructure from localhost using an OpenTofu container.

# It requires authentication to Azure via a service principle.
# Create the service principle via Azure CLI:
# az ad sp create-for-rbac --name "<name-of-service-principle>" --role="Contributor" --scopes="/subscriptions/<subscription-id>"
# (Note: it needs access to the whole subscription, so the infrastructure can be create in resource groups)
# Also needs "Storage Blob Data Contributor" role assignment to the service principle:
# https://stackoverflow.com/questions/52769758/azure-blob-storage-authorization-permission-mismatch-error-for-get-request-wit
# https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-access-azure-active-directory
# az role assignment create \
#   --role "Storage Blob Data Contributor"
#   --assignee <object_id_of_app*>
#   --scope /subscriptions/<subscription_id>/resourceGroups/<resource_group_name>/providers/Microsoft.Storage/storageAccounts/<storage_account_name>/blobServices/default/containers/<container_name>
# * object_id_of_app is not the allplication id.

# create the workspaces manually:
# ./scripts/start_infrastructure.sh # to get into the container
# tofu workspace new dev
# tofu workspace new stage
# tofu workspace new prod
# tofu init \
#     -backend-config="resource_group_name=${AZ_RESOURCE_GROUP_NAME}" \
#     -backend-config="storage_account_name=${AZ_STORAGE_ACCOUNT_NAME}" \
#     -backend-config="container_name=${AZ_CONTAINER_NAME}" \
#     -backend-config="key=${AZ_BACKEND_STATE_KEY}"'
#     -recoonfigure



echo "=== Running: deploy_infrastructure ==="


# Initialization:
REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
BRANCH_NAME=$(git branch --show-current)

cd $REPO_ROOT_DIR/infrastructure

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

This worked without entrypoint in docker compose file  -until tofu workspace select:
echo "=== tofu - version ==="
docker compose run --rm tofu --version
# docker compose exec tofu tofu --version
# docker compose exec tofu tofu --version


# echo "=== monitoring variables ==="
# # docker compose exec --entrypoint "echo $AZ_STORAGE_ACCOUNT_NAME" tofu 
# # docker compose exec tofu echo $ARM_CLIENT_ID
# docker compose run --rm --entrypoint '/bin/bash -c' tofu 'echo ${AZ_STORAGE_ACCOUNT_NAME}'
# # docker compose run --rm --entrypoint "pwd" tofu 


echo "=== tofu - init ==="
docker compose run --rm --entrypoint '/bin/sh -c' tofu 'tofu init \
    -backend-config="resource_group_name=${AZ_RESOURCE_GROUP_NAME}" \
    -backend-config="storage_account_name=${AZ_STORAGE_ACCOUNT_NAME}" \
    -backend-config="container_name=${AZ_CONTAINER_NAME}" \
    -backend-config="key=${AZ_BACKEND_STATE_KEY}"'
    
echo "=== tofu - workspace select ${WORKSPACE} ==="
docker compose run --rm -e "WORKSPACE=${WORKSPACE}" --entrypoint '/bin/sh -c' tofu 'tofu workspace select ${WORKSPACE}'



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