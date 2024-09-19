module "base_project_ECR" {
  source   = "../common/ecr_lambda"
  ecr_name = "role-based_app${var.env_suffix}"
}

module "base_project_lambda" {
  source      = "../common/lambda"
  ecr_uri     = module.base_project_ECR.ecr_uri_lambda
  tag         = var.IMAGE_TAG
  timeout     = 15
  memory_size = 512
  role_name   = "base_project_role${var.env_suffix}"
  func_name   = "bse_project_controller${var.env_suffix}"
}

module "base_project_lambda_api" {
  source                   = "../common/api-gateway"
  api_gw_name              = "role-based_app${var.env_suffix}"
  handler_lambda           = module.base_project_lambda.function
  stage_name               = var.stage_name
}
