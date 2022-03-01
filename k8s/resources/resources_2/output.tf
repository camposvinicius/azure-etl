data "azurerm_subscription" "subscription" {}

output "info_for_synapse_airflow_connection" {

  value = {
    clientID          = azuread_application.azure_application.application_id
    Secret            = nonsensitive(azuread_application_password.azure_application_password.value)
    FactoryName       = azurerm_data_factory.vinidatafactoryazure.name
    ResourceGroupName = azurerm_data_factory.vinidatafactoryazure.resource_group_name
    SubscriptionID    = data.azurerm_subscription.subscription.subscription_id
    TenantID          = data.azurerm_subscription.subscription.tenant_id
  }
  sensitive = false
}

output "info_for_databricks_airflow_connection" {
  value = {
    Extra = {
      "host" : tostring(azurerm_databricks_workspace.databricks_workspace.workspace_url),
      "token" : tostring(nonsensitive(databricks_token.databricks_token.token_value))
    }
  }
  sensitive = false
}

output "databricks_cluster_info" {
  value = {
    ClusterName  = databricks_cluster.databricks_cluster_single_node.cluster_name
    SparkVersion = databricks_cluster.databricks_cluster_single_node.spark_version
    ClusterId    = databricks_cluster.databricks_cluster_single_node.cluster_id
  }
}
