data "azurerm_client_config" "current" {}

data "azurerm_key_vault_secrets" "this" {
  key_vault_id = azurerm_key_vault.this.id
}

data "azurerm_key_vault_secret" "this" {
  for_each     = toset(data.azurerm_key_vault_secrets.this.names)
  name         = each.key
  key_vault_id = azurerm_key_vault.this.id
}