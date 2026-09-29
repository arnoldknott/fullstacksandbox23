# Provisions resources for full-stack sandbox 23

Run outside ci-pipeline and make it a manual trigger to proceed, after the outside-ci-run was successful.

## Deploying infrastructure

Needs manual approval before apply!

### ... from localhost:

```bash
./scripts/deploy_infrastructure.sh

```

in projects root directory

### ... in CI/CD pipeline


commit changes to infrastructure and push to repo.
follow the activity in Github Actions pipeline. 


## Structure of scripts

- code formatting before commit `tofu fmt`
- initializing `tofu init`
- selecting workspace based on git branch `tofu workspace select <dev|stage|prod>`
- generating the plan file `tofu plan`
- manual approval!
- applying the plan file `tofu apply`

## Rotating the application encryption key

The non-secret `encryption_rotation_revision` input controls intentional key rotation. Any change to the targeted environment's revision replaces the generated key and creates a new version of the existing `application-encryption-key` Key Vault secret. Existing secret versions remain available for decryption.

- For local infrastructure runs, increment `ENCRYPTION_ROTATION_REVISION` in `infrastructure/.env` and run the normal plan/deploy script from the branch corresponding to the intended Azure workspace. An unset value defaults to revision `1`.
- For GitHub Actions, set the repository/environment variable `ENCRYPTION_ROTATION_REVISION_DEV`, `ENCRYPTION_ROTATION_REVISION_STAGE`, or `ENCRYPTION_ROTATION_REVISION_PROD`, then run the normal branch deployment. Unset variables default to revision `1`.
- Inspect the OpenTofu plan before approval. It should replace `random_id.applicationEncryptionKey` and create a new Key Vault secret version, not delete the secret.

This mechanism applies to the Azure `dev`, `stage`, and `prod` workspaces. Localhost application and test encryption keys come from their application environment files and are rotated there instead. See the [application encryption contract](../docs/architecture/security/README.md#rotation-and-deployment) for deployment ordering and historical-key retention.
