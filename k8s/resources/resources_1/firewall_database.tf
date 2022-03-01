resource "azurerm_mssql_firewall_rule" "firewall_database" {
  name             = "FirewallSqlServer"
  server_id        = azurerm_mssql_server.sql_server.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"

  depends_on = [
    azurerm_mssql_database.vinidatabaseazure
  ]
}