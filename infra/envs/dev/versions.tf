terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "lexiconnect-tfstate-1771394861"
    key            = "lexiconnect/dev/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "lexiconnect-tf-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = "ap-south-1"
}

