resource "azurerm_storage_account" "storageacc_for_synapse" {
  name                     = "vinietlforsynapse"
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = "true"
}

resource "azurerm_storage_data_lake_gen2_filesystem" "datalake_gen2" {
  name               = "vinidatalakegen2"
  storage_account_id = azurerm_storage_account.storageacc_for_synapse.id
}

resource "azurerm_synapse_workspace" "vinisynapseworkspace" {
  name                                 = "vinisynapseworkspace"
  resource_group_name                  = var.resource_group_name
  location                             = var.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.datalake_gen2.id
  sql_administrator_login              = var.synapse_user
  sql_administrator_login_password     = var.synapse_pass

  tags = {
    Vini = "ETL-AZURE-SYNAPSE"
  }
}

resource "azurerm_synapse_sql_pool" "sql_pool_dw" {
  name                 = "sql_pool_dw_vini_etl"
  synapse_workspace_id = azurerm_synapse_workspace.vinisynapseworkspace.id
  sku_name             = "DW100c"
  create_mode          = "Default"

  depends_on = [
    azurerm_synapse_workspace.vinisynapseworkspace
  ]
}

resource "azurerm_synapse_firewall_rule" "firewall_synapse" {
  name                 = "AllowAllWindowsAzureIps"
  synapse_workspace_id = azurerm_synapse_workspace.vinisynapseworkspace.id
  start_ip_address     = "0.0.0.0"
  end_ip_address       = "0.0.0.0"

  depends_on = [
    azurerm_synapse_workspace.vinisynapseworkspace
  ]
}