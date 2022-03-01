resource "azurerm_data_factory_dataset_sql_server_table" "SqlServerCryptoTable" {
  name                = "SqlServerCryptoTable"
  table_name          = "crypto"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.vinidatafactoryazure.id
  linked_service_name = azurerm_data_factory_linked_service_sql_server.SqlServerToBronzeBlobContainer.name
}

resource "azurerm_data_factory_dataset_parquet" "AzureBlobStorageBronze" {
  name                = "AzureBlobStorageBronze"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.vinidatafactoryazure.id
  linked_service_name = azurerm_data_factory_linked_service_azure_blob_storage.AzureBlobStorageBronze.name
  compression_codec   = "snappy"

  azure_blob_storage_location {
    container = "bronze"
    path      = "data"
    filename  = "crypto.parquet"
  }
}