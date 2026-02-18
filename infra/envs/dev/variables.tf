variable "project" {
  type    = string
  default = "lexiconnect"
}

variable "env" {
  type    = string
  default = "dev"
}

variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.0.0/24", "10.0.1.0/24"]
}

variable "private_db_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "key_name" {
  description = "Existing EC2 key pair name in ap-south-1"
  type        = string
}

variable "repo_url" {
  description = "Git repo URL (public). If private, we'll switch to deploy keys later."
  type        = string
}

variable "db_name" {
  type    = string
  default = "lexiconnect"
}

variable "db_username" {
  type    = string
  default = "lexiconnect"
}

variable "db_password" {
  description = "RDS master password (use TF_VAR_db_password env var, do not commit)"
  type        = string
  sensitive   = true
}

