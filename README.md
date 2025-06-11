# demo "DEVNET-2303"

If you want to try to run each step individually, here's the steps

## Terraform 

### Plan
cd DEVNET-2303/terraform

terraform init

terraform plan -out=tfplan

### Build
cd DEVNET-2303/terraform

terraform apply -auto-approve tfplan

terraform output -json > ./terraform_output.json

## Ansible

### Setup
apt-get update && apt-get install -y sshpass openssh-client

pip install ansible netmiko pyyaml jinja2 paramiko cmlutils virl2-client ansible-pylibssh

ansible-galaxy collection install cisco.ios cisco.nxos ansible.netcommon

cd DEVNET-2303/ansible

ansible-playbook -i inv/hosts.ini main.yml -vvv

## PyATS

### Run
apt-get update && apt-get install -y telnet

pip install pyats genie tabulate netmiko rich

cd DEVNET-2303/pyats

easypy run_tests.py -testbed_file testbed.yml

### Cleanup
cd DEVNET-2303/terraform
terraform init
terraform destroy -auto-approve

