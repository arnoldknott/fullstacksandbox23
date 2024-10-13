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