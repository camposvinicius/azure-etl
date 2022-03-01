data "azuread_client_config" "current" {}

resource "azuread_application" "azure_application" {
  display_name = "RunADFPipelineApplication"
  owners       = [data.azuread_client_config.current.object_id]

  depends_on = [
    azurerm_data_factory.vinidatafactoryazure
  ]
}

resource "azuread_application_password" "azure_application_password" {
  display_name          = "DataFactoryPassword"
  application_object_id = azuread_application.azure_application.object_id

  depends_on = [
    azurerm_data_factory.vinidatafactoryazure
  ]
}

resource "azuread_service_principal" "service_principal" {
  application_id               = azuread_application.azure_application.application_id
  app_role_assignment_required = false
  owners                       = [data.azuread_client_config.current.object_id]
}


