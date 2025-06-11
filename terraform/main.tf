# Terraform Configuration for Cisco Modeling Lab
# File: main.tf

terraform {
  required_providers {
    cml2 = {
      source  = "CiscoDevNet/cml2"
      version = "~> 0.8.0"
    }
  }
}

# Define variables
variable "CML_USERNAME" {
  description = "Username for CML2"
  type        = string
  sensitive   = true
  default = "developer"
}

variable "CML_PASSWORD" {
  description = "Password for CML2"
  type        = string
  sensitive   = true
  default = "C1sco12345"
}

variable "CML_HOST" {
  description = "Hostname/IP of CML2 server"
  type        = string
  default = "https://10.10.20.161"
}

# Provider configuration
provider "cml2" {
  address  = var.CML_HOST
  username = var.CML_USERNAME
  password = var.CML_PASSWORD
  skip_verify = true
}

# Create a lab
resource "cml2_lifecycle" "this" {
  topology = file("topology.yaml")
} 

