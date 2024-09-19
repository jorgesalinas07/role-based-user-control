variable "ecr_uri" {
  type = string
}

variable "tag" {
  type = string
}

variable "timeout" {
  type = number
}

variable "memory_size" {
  type = number
}

variable "role_name" {
  type = string
}

variable "func_name" {
  type = string
}

variable "permissions" {
  description = "Add aditional permissions to the lambda function"
  default     = []
}

variable "env_variables" {
  default = []
}

variable "source_arn" {
  type    = string
  default = ""
}
