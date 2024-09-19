terraform {
  required_providers {

    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.9.0"
    }

  }
  backend "s3" {
    bucket  = "role-based-app-backend-tfstate-79eb25"
    key     = "global/s3/stage.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = "us-east-1"
}

module "environment" {
  source     = "../environment"
  env_suffix = "_stg"
  stage_name = "stage"
  IMAGE_TAG  = var.IMAGE_TAG
}
