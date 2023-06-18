locals {
  location    = "East US 2"
  common_name = "bs-ca"
  common_tags = {
    owner     = "Pat Lafferty"
    managedBy = "Terraform"
  }

  vnet_size = split("/", azurerm_virtual_network.this.address_space[0])[1]
  subnet_prefix = cidrsubnet(
    azurerm_virtual_network.this.address_space[0],
    var.network.subnet_size - local.vnet_size,
    0
  )
}