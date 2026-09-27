variable "aws_region" {
  description = "AWS region used for the OpsPilot infrastructure."
  type        = string
  default     = "ap-south-1"
}

variable "aws_profile" {
  description = "Local AWS CLI profile used by Terraform. CI will use workload credentials later."
  type        = string
  default     = "opspilot"
}

variable "project_name" {
  description = "Project name used in AWS resource names and tags."
  type        = string
  default     = "opspilot-ai"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the OpsPilot VPC."
  type        = string
  default     = "10.42.0.0/16"
}
