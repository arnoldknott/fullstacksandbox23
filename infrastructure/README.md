# Provisions resources for full-stack sandbox 23

## Initializing terraform

Add initialization command of terraform here!

## Code formatting - run before committing!

```bash
tofu fmt
```

## Using workspaces

```bash
tofu workspace select dev
tofu workspace select stage
tofu workspace select prod
```

## Generating the plan file

```bash
tofu plan <environment>.tfplan
```

## Applying the plan file

```bash
tofu apply --auto-approve <environment>.tfplan
```