variable "api_gw_name" {
  type        = string
  description = "API Gateway Name"
}

variable "handler_lambda" {
  description = "Lambda Function resource for cors handler"
}

variable "stage_name" {
  type    = string
  default = "prod"
}
