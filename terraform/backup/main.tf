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
resource "cml2_lab" "network_lab" {
  title       = "Network Automation Lab"
  description = "Lab created by Terraform CI/CD pipeline"
}

# Create a router node
resource "cml2_node" "router1" {
  lab_id         = cml2_lab.network_lab.id
  label          = "R1"
  nodedefinition = "iosv"
  configuration  = file("${path.module}/configs/r1_base.cfg")
  x              = 0
  y              = 0
}

# Create a second router node
resource "cml2_node" "router2" {
  lab_id         = cml2_lab.network_lab.id
  label          = "R2"
  nodedefinition = "iosv"
  configuration  = file("${path.module}/configs/r2_base.cfg")
  x              = 200
  y              = 0
}

# Create a switch node
resource "cml2_node" "switch1" {
  lab_id         = cml2_lab.network_lab.id
  label          = "SW1"
  nodedefinition = "iosvl2"
  configuration  = file("${path.module}/configs/sw1_base.cfg")
  x              = 100
  y              = 100
}

# Create link between R1 and R2
resource "cml2_link" "r1_to_r2" {
  lab_id = cml2_lab.network_lab.id
  node_a = cml2_node.router1.id
  node_b = cml2_node.router2.id
}

# Create link between R1 and SW1
resource "cml2_link" "r1_to_sw1" {
  lab_id = cml2_lab.network_lab.id
  node_a = cml2_node.router1.id
  node_b = cml2_node.switch1.id
}

# Create link between R2 and SW1
resource "cml2_link" "r2_to_sw1" {
  lab_id = cml2_lab.network_lab.id
  node_a = cml2_node.router2.id
  node_b = cml2_node.switch1.id
}

# Start the lab
resource "cml2_lifecycle" "lab_state" {
  lab_id = cml2_lab.network_lab.id
  depends_on = [
    cml2_node.router1,
    cml2_node.router2,
    cml2_node.switch1,
    cml2_link.r1_to_r2,
    cml2_link.r1_to_sw1,
    cml2_link.r2_to_sw1,
  ]
  state  = "STARTED"
}

# Output lab details
output "lab_id" {
  value = cml2_lab.network_lab.id
}

output "router1_ip" {
  value = cml2_lifecycle.lab_state.nodes[cml2_node.router1.id].interfaces[0].ip4[0] 
}

output "router2_ip" {
  value = cml2_lifecycle.lab_state.nodes[cml2_node.router2.id].interfaces[0].ip4[0]
}

output "switch1_ip" {
  value = cml2_lifecycle.lab_state.nodes[cml2_node.switch1.id].interfaces[0].ip4[0]
}

