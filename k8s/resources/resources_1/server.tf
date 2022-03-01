resource "azurerm_mssql_server" "sql_server" {
  name                          = "sqlserver-vinietlazure"
  resource_group_name           = var.resource_group_name
  location                      = var.location
  version                       = "12.0"
  administrator_login           = var.sqlserver_user
  administrator_login_password  = var.sqlserver_pass
  minimum_tls_version           = "1.2"
  public_network_access_enabled = true

  tags = {
    Vini = "ETL-AZURE"
  }
}