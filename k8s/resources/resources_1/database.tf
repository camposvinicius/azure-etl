resource "azurerm_mssql_database" "vinidatabaseazure" {
  name                 = "database-sqlserver-vinietlazure"
  server_id            = azurerm_mssql_server.sql_server.id
  collation            = "SQL_Latin1_General_CP1_CI_AS"
  license_type         = "LicenseIncluded"
  max_size_gb          = 1
  storage_account_type = "LRS"

  tags = {
    Vini = "ETL-AZURE"
  }

  depends_on = [
    azurerm_mssql_server.sql_server
  ]

}