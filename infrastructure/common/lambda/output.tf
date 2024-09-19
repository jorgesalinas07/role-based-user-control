output "function" {
  value = resource.aws_lambda_function.func
}

output "func_role" {
  value = resource.aws_iam_role.func_role
}
