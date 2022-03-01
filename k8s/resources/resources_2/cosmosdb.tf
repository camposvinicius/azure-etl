resource "azurerm_cosmosdb_account" "db" {
  name                = "vinicosmosdbetlazure"
  location            = var.location
  resource_group_name = var.resource_group_name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  enable_free_tier              = true
  public_network_access_enabled = true
  enable_automatic_failover     = true

  consistency_policy {
    consistency_level       = "BoundedStaleness"
    max_interval_in_seconds = 300
    max_staleness_prefix    = 100000
  }

  geo_location {
    location          = var.location
    failover_priority = 0
  }
}

resource "azurerm_cosmosdb_sql_database" "cosmosdb_sql_database" {
  name                = "cosmosdbdatabase"
  resource_group_name = var.resource_group_name
  account_name        = azurerm_cosmosdb_account.db.name
  throughput          = 400

  depends_on = [
    azurerm_cosmosdb_account.db
  ]
}


resource "azurerm_cosmosdb_sql_container" "cosmosdb_container" {
  name                  = "cosmosdbcontainer"
  resource_group_name   = var.resource_group_name
  account_name          = azurerm_cosmosdb_account.db.name
  database_name         = azurerm_cosmosdb_sql_database.cosmosdb_sql_database.name
  partition_key_path    = "/data"
  partition_key_version = 1
  throughput            = 400

  depends_on = [
    azurerm_cosmosdb_sql_database.cosmosdb_sql_database
  ]
}