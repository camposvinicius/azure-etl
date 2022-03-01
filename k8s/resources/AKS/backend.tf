terraform {
  backend "azurerm" {
    resource_group_name  = "vinietlazure"
    storage_account_name = "vinietlazure"
    container_name       = "tfstateaks"
    key                  = "terraform/tfstate"
  }
}