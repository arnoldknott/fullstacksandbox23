# ssh into the machine with `ssh -i <path to private key> adminuser@<public ip>`
resource "azurerm_linux_virtual_machine" "adminVirtualMachine" {
  count               = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  name                = "${var.project_name}-adminVirtualMachine-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location
  size                = "Standard_B1ls"
  admin_username      = "adminuser"
  network_interface_ids = [
    azurerm_network_interface.adminVirtualMachineNetworkInterface[0].id,
  ]
  computer_name         = "adminVM"
  patch_assessment_mode = "AutomaticByPlatform" #"AutomaticByPlatform" -> "ImageDefault"

  lifecycle {
    ignore_changes = [identity]
  }

  os_disk {
    name                 = "${var.project_name}-adminVirtualMachineOsDisk-${terraform.workspace}"
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  # get list of avialable images with `az vm image list -p Canonical -f ubuntu-24_04-lts --all -o table`
  source_image_reference {
    publisher = "Canonical"
    offer     = "ubuntu-24_04-lts" # previous: "0001-com-ubuntu-server-jammy"#
    sku       = "server"           # previous: "22_04-lts-gen2"#
    version   = "latest"
  }

  admin_ssh_key {
    username   = "adminuser"
    public_key = file(var.public_ssh_key_path)
  }

  custom_data = filebase64("adminVirtualMachine.sh")

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}