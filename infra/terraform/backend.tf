terraform {
  backend "s3" {
    bucket       = "opspilot-ai-tfstate-577638393088-ap-south-1"
    key          = "opspilot/dev/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true
  }
}
