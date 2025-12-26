#!/bin/bash

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
az account get-access-token --resource https://management.azure.com/ --output json > .azure/azure_token.json
cp -fR ~/.azure/* .azure/

echo ""
echo "=== tofu - version ==="
docker compose run --rm --entrypoint 'tofu' tofu --version

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
docker compose run --rm -e "WORKSPACE=${WORKSPACE}" --entrypoint '/bin/sh -c' tofu 'cp -fR .azure/ ~/.azure &&
tofu workspace select -or-create \
        -var "azure_tenant_id=${AZURE_TENANT_ID}" \
        -var "azure_client_id=${AZURE_CLIENT_ID}" \
        -var "azure_subscription_id=${AZURE_SUBSCRIPTION_ID}" \
        ${WORKSPACE}'
echo "selected workspace:"
docker compose run --rm --entrypoint 'tofu' tofu workspace show

echo ""
echo "=== entering the tofu container with \$TOFU_VARIABLES and 't' function ==="
docker compose run --rm -it --entrypoint "/bin/sh" tofu -c '
cp -fR .azure/ ~/.azure
export TOFU_VARIABLES="-var \"azure_tenant_id=${AZURE_TENANT_ID}\" -var \"azure_client_id=${AZURE_CLIENT_ID}\" -var \"azure_subscription_id=${AZURE_SUBSCRIPTION_ID}\" -var \"developer_localhost_object_id=${DEVELOPER_LOCALHOST_OBJECT_ID}\" -var \"managed_identity_github_actions_object_id=${MANAGED_IDENTITY_GITHUB_ACTIONS_OBJECT_ID}\" -var \"project_name=${PROJECT_NAME}\" -var \"project_short_name=${PROJECT_SHORT_NAME}\" -var \"project_repository_name=${PROJECT_REPOSITORY_NAME}\" -var \"costcenter=${COSTCENTER}\" -var \"owner_name=${OWNER_NAME}\" -var \"budget_notification_email=${BUDGET_NOTIFICATION_EMAIL}\" -var \"owner_object_id=${OWNER_OBJECT_ID}\" -var \"postgres_port=${POSTGRES_PORT}\" -var \"pgadmin_default_email=${PGADMIN_DEFAULT_EMAIL}\" -var \"redis_port=${REDIS_PORT}\" -var \"redis_insight_port=${REDIS_INSIGHT_PORT}\" -var \"public_ssh_key_path=${PUBLIC_SSH_KEY_PATH}\""
echo ""
echo "Environment variable TOFU_VARIABLES is set with all required -var flags."
echo "Usage: tofu plan \$TOFU_VARIABLES"
echo "       tofu apply \$TOFU_VARIABLES"
echo "       tofu import \$TOFU_VARIABLES '\''resource[0]'\'' id"
echo "See the current content with echo \$TOFU_VARIABLES"
echo ""
cat > ~/.tofu_alias << TOFUALIAS
t() {
    tofu "\$@" $TOFU_VARIABLES
}
TOFUALIAS
echo "Function '\''t'\'' loaded."
echo "Usage: t plan"
echo "       t apply,"
echo "       t state rm '\''resource[0]'\''"
echo "Try it with '\''t validate'\''."
echo ""
ENV=~/.tofu_alias /bin/sh
'
