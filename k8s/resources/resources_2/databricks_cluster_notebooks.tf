data "databricks_node_type" "smallest" {
  provider   = databricks.created_workspace
  local_disk = true

  depends_on = [
    azurerm_databricks_workspace.databricks_workspace,
    databricks_token.databricks_token
  ]
}

data "databricks_spark_version" "components_version" {
  provider          = databricks.created_workspace
  latest            = false
  long_term_support = true
  scala             = "2.12"
  spark_version     = "3.1.2"
}

resource "databricks_cluster" "databricks_cluster_single_node" {
  provider                = databricks.created_workspace
  cluster_name            = "CLUSTER-DATABRICKS-VINI-ETL-AZURE"
  spark_version           = data.databricks_spark_version.components_version.id
  node_type_id            = data.databricks_node_type.smallest.id
  autotermination_minutes = 20

  autoscale {
    min_workers = 1
    max_workers = 2
  }

  spark_conf = {
    # Single-node
    "spark.master" : "local[*, 4]"
    "spark.databricks.cluster.profile" : "singleNode"
    "spark.databricks.passthrough.enabled" : "true"
    "spark.databricks.repl.allowedLanguages" : "scala,sql"
  }

  library {
    maven {
      coordinates = "com.azure.cosmos.spark:azure-cosmos-spark_3-1_2-12:4.6.2"
    }
  }

  azure_attributes {
    availability       = "SPOT_AZURE"
    spot_bid_max_price = -1
  }

  custom_tags = {
    "Vini" = "ETL-AZURE-DATABRICKS"
  }

  depends_on = [
    data.databricks_node_type.smallest,
    azurerm_databricks_workspace.databricks_workspace,
    databricks_token.databricks_token
  ]
}

resource "databricks_notebook" "upload_notebooks" {

  provider = databricks.created_workspace

  for_each = fileset("../notebooks/", "*.dbc")
  path     = "/ViniEtlAzure/Notebooks/${each.value}"
  source   = "../notebooks/${each.value}"
  language = "SCALA"

  depends_on = [
    data.databricks_node_type.smallest,
    azurerm_databricks_workspace.databricks_workspace,
    databricks_token.databricks_token,
    databricks_cluster.databricks_cluster_single_node
  ]
}
