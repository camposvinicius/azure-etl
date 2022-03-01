resource "azurerm_data_factory" "vinidatafactoryazure" {
  name                   = "vinidatafactoryazure"
  location               = var.location
  resource_group_name    = var.resource_group_name
  public_network_enabled = true

  tags = {
    Vini = "ETL-AZURE"
  }

}

resource "azurerm_data_factory_pipeline" "CopySqlServerToBronzeBlobContainer" {
  name                = "CopySqlServerToBronzeBlobContainer"
  resource_group_name = var.resource_group_name
  data_factory_id     = azurerm_data_factory.vinidatafactoryazure.id

  activities_json = <<JSON
[
  {
    "name": "CopySqlServerToBronzeBlobContainer",
    "type": "Copy",
    "policy": {
        "timeout": "7.00:00:00",
        "retry": 0,
        "retryIntervalInSeconds": 30,
        "secureOutput": false,
        "secureInput": false
    },
    "typeProperties": {
        "source": {
            "type": "SqlServerSource",
            "queryTimeout": "02:00:00",
            "partitionOption": "None"
        },
        "sink": {
            "type": "ParquetSink",
            "storeSettings": {
                "type": "AzureBlobStorageWriteSettings"
            },
            "formatSettings": {
                "type": "ParquetWriteSettings"
            }
        },
        "enableStaging": false
    },
    "inputs": [
        {
            "referenceName": "SqlServerCryptoTable",
            "type": "DatasetReference"
        }
    ],
    "outputs": [
        {
            "referenceName": "AzureBlobStorageBronze",
            "type": "DatasetReference"
        }
    ]
  }
]
  JSON

  depends_on = [
    azurerm_data_factory.vinidatafactoryazure,
    azurerm_data_factory_linked_service_sql_server.SqlServerToBronzeBlobContainer,
    azurerm_data_factory_linked_service_azure_blob_storage.AzureBlobStorageBronze
  ]

}

