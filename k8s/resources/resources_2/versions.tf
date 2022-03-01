terraform {
  required_providers {

    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 2.95.0"
    }

    azuread = {
      source  = "hashicorp/azuread"
      version = ">= 2.17.0"
    }

    databricks = {
      source  = "databrickslabs/databricks"
      version = ">= 0.4.8"
    }

    null = {
      version = ">= 3.1.0"
      source  = "hashicorp/null"
    }
  }

  required_version = ">= 0.14"
}