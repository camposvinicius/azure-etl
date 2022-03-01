provider "azurerm" {
  features {}
}

provider "databricks" {
  alias                       = "created_workspace"
  host                        = azurerm_databricks_workspace.databricks_workspace.workspace_url
  azure_workspace_resource_id = azurerm_databricks_workspace.databricks_workspace.id
}