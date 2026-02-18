# Infra README

Terraform code for LexiConnect lives in `infra/envs/dev`.

## Commands

```bash
cd infra/envs/dev
terraform init -reconfigure
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Destroy:

```bash
cd infra/envs/dev
terraform destroy
```

## Remote State

Configured in `infra/envs/dev/versions.tf`:
- S3 bucket: `lexiconnect-tfstate-1771394861`
- DynamoDB lock table: `lexiconnect-tf-locks`
- Key: `lexiconnect/dev/terraform.tfstate`
- Region: `ap-south-1`

## Outputs

```bash
cd infra/envs/dev
terraform output
```

Expected key outputs:
- `alb_dns_name`
- `asg_name`
- `rds_endpoint`

## Cost Profile

- NAT Gateway intentionally omitted to reduce recurring cost.
- Minimal classes/sizes used for credit-safe operation.
- Destroy stacks when idle.

## Notes

Do not commit secrets. Provide sensitive values through environment variables or secure CI secret stores.

