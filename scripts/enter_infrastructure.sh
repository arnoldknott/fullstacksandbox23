#!/bin/bash

REPO_ROOT_DIR=$(git rev-parse --show-toplevel)
cd $REPO_ROOT_DIR/infrastructure

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
echo "=== entering the tofu container ==="
# docker compose run --rm -it --entrypoint "cp -fR .azure/ ~/.azure && /bin/sh" tofu
docker compose run --rm -it --entrypoint "/bin/sh" tofu