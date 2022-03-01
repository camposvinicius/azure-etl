data "azuread_service_principals" "service_principal_databricks" {
  display_names = [
    "Databricks Resource Provider"
  ]

  depends_on = [
    azurerm_databricks_workspace.databricks_workspace
  ]
}

resource "azurerm_role_assignment" "role_assignment_1" {
  scope                = "/subscriptions/your-code-global-admin"
  role_definition_name = "Owner"
  principal_id         = azuread_service_principal.service_principal.object_id

  depends_on = [
    azuread_application.azure_application,
    azuread_application_password.azure_application_password,
    azuread_service_principal.service_principal,
    data.azuread_service_principals.service_principal_databricks
  ]
}

resource "azurerm_role_assignment" "role_assignment_2" {
  scope                = "/subscriptions/your-code-global-admin"
  role_definition_name = "Owner"
  principal_id         = data.azuread_service_principals.service_principal_databricks.object_ids[0]

  depends_on = [
    azuread_application.azure_application,
    azuread_application_password.azure_application_password,
    azuread_service_principal.service_principal,
    data.azuread_service_principals.service_principal_databricks
  ]
}

resource "azurerm_role_assignment" "role_assignment_3" {
  scope                = "/subscriptions/your-code-global-admin"
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = data.azuread_service_principals.service_principal_databricks.object_ids[0]

  depends_on = [
    azuread_application.azure_application,
    azuread_application_password.azure_application_password,
    azuread_service_principal.service_principal,
    data.azuread_service_principals.service_principal_databricks
  ]
}

resource "azurerm_role_assignment" "role_assignment_4" {
  scope                = "/subscriptions/your-code-global-admin"
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = azuread_service_principal.service_principal.object_id

  depends_on = [
    azuread_application.azure_application,
    azuread_application_password.azure_application_password,
    azuread_service_principal.service_principal,
    data.azuread_service_principals.service_principal_databricks
  ]
}