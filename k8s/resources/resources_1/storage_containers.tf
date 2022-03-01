resource "azurerm_storage_container" "containers" {
  for_each              = toset(var.containers_names)
  name                  = each.key
  storage_account_name  = var.storage_account_name
  container_access_type = "container"
}
