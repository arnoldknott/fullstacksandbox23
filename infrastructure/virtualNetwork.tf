# from https://levelup.gitconnected.com/how-to-connect-azure-container-apps-to-a-postgresql-flexible-server-using-terraform-68e108fe8dd4
# code structure there:
#
# TBD: remove all of theis again, when decrypted:
#
# RESOURCES:
#   =>  Subnet
#       => azurerm_subnet
#   =>  Private DNS Zone
#       => azurerm_private_dns_zone
#       => azurerm_private_dns_zone_virtual_network_link
#   =>  Postgres Flexible Server
#       => azurerm_postgresql_flexible_server
#   =>  Container Environment
#       => azurerm_log_analytics_workspace
#       => azurerm_container_environment
#   =>  Container App
#       => azurerm_container_app
#
# 2 MODULES
#   =>  Network
#       =>  virtual_network ?¿?MISSING?¿? or is it the ?¿?private_dns_zone?¿?
#       =>  subnet for postgresql
#       =>  subnet for conatainer_app
#       =>  private_dns_zone
#   =>  Main
#       =>  resource_group
#       =>  container_app_environment
#       =>  postgresql_flexible_server
#       =>  container_app
#
# OK - LET's BUILD:

# Virtual network - 2 subnets - private DNS zone for postgres? - postgres flex-server - container stuff already exists!

resource "azurerm_virtual_network" "virtualNetwork" {
  name                = "${var.project_name}-virtualNetwork-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location
  address_space       = ["10.0.0.0/8"]

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

resource "azurerm_subnet" "subnetContainerapp" {
  name                 = "${var.project_name}-subnetContainerapp-${terraform.workspace}"
  resource_group_name  = azurerm_resource_group.resourceGroup.name
  virtual_network_name = azurerm_virtual_network.virtualNetwork.name
  address_prefixes     = ["10.0.0.0/22"]

  lifecycle {
    ignore_changes = [private_endpoint_network_policies]
  }
}

resource "azurerm_subnet" "subnetPostgres" {
  name                 = "${var.project_name}-subnetPostgres-${terraform.workspace}"
  resource_group_name  = azurerm_resource_group.resourceGroup.name
  virtual_network_name = azurerm_virtual_network.virtualNetwork.name
  address_prefixes     = ["10.0.8.0/24"]
  service_endpoints    = ["Microsoft.Storage"]

  lifecycle {
    ignore_changes = [private_endpoint_network_policies]
  }

  delegation {
    name = "${var.project_name}-subnetPostgresDelegation-${terraform.workspace}"
    service_delegation {
      name    = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

resource "azurerm_subnet" "subnetAdminVirtualMachine" {
  name                 = "${var.project_name}-adminVirtualMachine-${terraform.workspace}"
  resource_group_name  = azurerm_resource_group.resourceGroup.name
  virtual_network_name = azurerm_virtual_network.virtualNetwork.name
  address_prefixes     = ["10.0.10.0/24"]

  lifecycle {
    ignore_changes = [private_endpoint_network_policies]
  }
}

# resource "azurerm_subnet" "subnetFileStorage" {
#   name                 = "${var.project_name}-fileStorage-${terraform.workspace}"
#   resource_group_name  = azurerm_resource_group.resourceGroup.name
#   virtual_network_name = azurerm_virtual_network.virtualNetwork.name
#   address_prefixes     = ["10.0.12.0/24"]
#   service_endpoints    = ["Microsoft.Storage"]
# }

# resource "azurerm_subnet" "subnetPrivateLinks" {
#   name                 = "${var.project_name}-privateLinks-${terraform.workspace}"
#   resource_group_name  = azurerm_resource_group.resourceGroup.name
#   virtual_network_name = azurerm_virtual_network.virtualNetwork.name
#   address_prefixes     = ["10.0.14.0/24"]
#   private_link_service_network_policies_enabled = true
#   private_endpoint_network_policies_enabled = true
# }

resource "azurerm_private_dns_zone" "privateDNSZone" {
  name                = "${var.project_short_name}-privatednszone-${terraform.workspace}.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.resourceGroup.name

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

resource "azurerm_private_dns_zone_virtual_network_link" "privateDNSZoneLink" {
  name                  = "${var.project_short_name}vnetlink"
  private_dns_zone_name = azurerm_private_dns_zone.privateDNSZone.name
  virtual_network_id    = azurerm_virtual_network.virtualNetwork.id
  resource_group_name   = azurerm_resource_group.resourceGroup.name
}



resource "azurerm_public_ip" "adminVirtualMachineIPadress" {
  count               = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  name                = "${var.project_name}-adminVirtualMachineIPadress-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location
  allocation_method   = "Static"

  sku = "Standard"

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

resource "azurerm_network_interface" "adminVirtualMachineNetworkInterface" {
  count               = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  name                = "${var.project_name}-virtualMachineNetworkInterface-${terraform.workspace}"
  resource_group_name = azurerm_resource_group.resourceGroup.name
  location            = azurerm_resource_group.resourceGroup.location

  ip_configuration {
    name                          = "${var.project_name}-virtualMachineIPConfiguration-${terraform.workspace}"
    subnet_id                     = azurerm_subnet.subnetAdminVirtualMachine.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.adminVirtualMachineIPadress[0].id
  }

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}


resource "azurerm_network_security_group" "adminVirtualMachineNetworkSecurityGroup" {
  count               = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  name                = "${var.project_name}-virtualMachineNetworkSecurityGroup-${terraform.workspace}"
  location            = azurerm_resource_group.resourceGroup.location
  resource_group_name = azurerm_resource_group.resourceGroup.name

  security_rule {
    name                       = "${var.project_name}-virtualMachineNetworkSecurityGroup-${terraform.workspace}-rule-ssh"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "${var.project_name}-virtualMachineNetworkSecurityGroup-${terraform.workspace}-rule-ping"
    priority                   = 200
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Icmp"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    Costcenter  = var.costcenter
    Owner       = var.owner_name
    Environment = terraform.workspace
  }
}

resource "azurerm_subnet_network_security_group_association" "adminVirtualMachineNetworkSecurityGroupAssociation" {
  count               = terraform.workspace == "dev" || terraform.workspace == "stage" ? 1 : 0
  subnet_id                 = azurerm_subnet.subnetAdminVirtualMachine.id
  network_security_group_id = azurerm_network_security_group.adminVirtualMachineNetworkSecurityGroup[0].id
}
