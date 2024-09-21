# Provisions resources for full-stack sandbox 23

## Initializing terraform

## Code formatting - run before committing!

```bash
terraform fmt
```

## Using workspaces

```bash
terraform workspace select dev
terraform workspace select stage
terraform workspace select prod
```

## Generating the plan file

```bash
terraform plan <environment>.tfplan
```

## Applying the plan file

```bash
terraform apply --auto-approve <environment>.tfplan
```