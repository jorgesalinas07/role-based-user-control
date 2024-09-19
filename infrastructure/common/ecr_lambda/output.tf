output "ecr" {
  value = resource.aws_ecr_repository.ecr
}

output "ecr_uri_lambda" {
  value = resource.aws_ecr_repository.ecr.repository_url
}
