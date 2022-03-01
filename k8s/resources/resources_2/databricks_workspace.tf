resource "azurerm_databricks_workspace" "databricks_workspace" {
  name                = "vinidatabricksworkspace"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "trial"

  tags = {
    Vini = "ETL-AZURE-DATABRICKS"
  }
}

resource "databricks_token" "databricks_token" {
  provider = databricks.created_workspace
  comment  = "The token Databricks"

  depends_on = [
    azurerm_databricks_workspace.databricks_workspace,
    azurerm_role_assignment.role_assignment_1,
    azurerm_role_assignment.role_assignment_2,
    azurerm_role_assignment.role_assignment_3,
    azurerm_role_assignment.role_assignment_4
  ]
}

