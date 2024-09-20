variable "env_suffix" {
  type    = string
  default = ""
}

variable "IMAGE_TAG" {
  description = "ECR Image tag"
  type        = string
  default     = "latest"
}

variable "stage_name" {
  type    = string
  default = "prod"
}
