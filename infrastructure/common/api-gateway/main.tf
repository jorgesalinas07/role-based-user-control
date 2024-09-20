resource "aws_api_gateway_rest_api" "rest-api" {
  name = var.api_gw_name
}

resource "aws_api_gateway_resource" "api-gw" {
  path_part   = "{proxy+}"
  rest_api_id = aws_api_gateway_rest_api.rest-api.id
  parent_id   = aws_api_gateway_rest_api.rest-api.root_resource_id
}

resource "aws_api_gateway_method" "api-gw-method" {
  rest_api_id   = aws_api_gateway_rest_api.rest-api.id
  resource_id   = aws_api_gateway_resource.api-gw.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "api-gw-integration" {
  rest_api_id             = aws_api_gateway_rest_api.rest-api.id
  resource_id             = aws_api_gateway_resource.api-gw.id
  http_method             = aws_api_gateway_method.api-gw-method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.handler_lambda.invoke_arn
}

resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id     = aws_api_gateway_rest_api.rest-api.id
  resource_id     = aws_api_gateway_resource.api-gw.id
  http_method     = aws_api_gateway_method.api-gw-method.http_method
  status_code     = "200"
  response_models = { "application/json" = "Empty" }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Origin"  = true,
    "method.response.header.Access-Control-Allow-Methods" = true
  }
}

resource "aws_api_gateway_integration_response" "IntegrationResponse" {
  depends_on = [
    aws_api_gateway_integration.api-gw-integration
  ]
  rest_api_id = aws_api_gateway_rest_api.rest-api.id
  resource_id = aws_api_gateway_resource.api-gw.id
  http_method = aws_api_gateway_method.api-gw-method.http_method
  status_code = aws_api_gateway_method_response.response_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "integration.response.body.headers.Access-Control-Allow-Headers"
    "method.response.header.Access-Control-Allow-Origin"  = "integration.response.body.headers.Access-Control-Allow-Origin"
    "method.response.header.Access-Control-Allow-Methods" = "integration.response.body.headers.Access-Control-Allow-Methods"
  }
}

resource "aws_api_gateway_deployment" "api-gw-deployment" {
  rest_api_id = aws_api_gateway_rest_api.rest-api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.rest-api.body,
      aws_api_gateway_resource.api-gw.id,
      aws_api_gateway_method.api-gw-method.id,
      aws_api_gateway_integration.api-gw-integration.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "api-gw-stage" {
  deployment_id = aws_api_gateway_deployment.api-gw-deployment.id
  rest_api_id   = aws_api_gateway_rest_api.rest-api.id
  stage_name    = "stage"
}
