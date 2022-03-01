resource "azurerm_data_factory_linked_service_sql_server" "SqlServerToBronzeBlobContainer" {
  name                = "SqlServerToBronzeBlobContainer"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.vinidatafactoryazure.id
  connection_string   = "integrated security=False;data source=sqlserver-vinietlazure.database.windows.net;initial catalog=database-sqlserver-vinietlazure;user id=vinietlazure; pwd=A1b2C3d4"

}

resource "azurerm_data_factory_linked_service_azure_blob_storage" "AzureBlobStorageBronze" {
  name                = "AzureBlobStorageBronze"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.vinidatafactoryazure.id
  connection_string   = "DefaultEndpointsProtocol=https;AccountName=vinietlazure;AccountKey=your-account-key;EndpointSuffix=core.windows.net"

}
