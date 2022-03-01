resource "azurerm_kubernetes_cluster" "aks_cluster" {
  name                = "cluster-aks-${var.resource_group_name}"
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = "k8s-${var.resource_group_name}"

  default_node_pool {
    name                = "default"
    vm_size             = "Standard_D4_v2"
    enable_auto_scaling = true
    max_count           = 2
    min_count           = 1
    node_count          = 1
  }

  public_network_access_enabled   = true
  api_server_authorized_ip_ranges = ["0.0.0.0/0"]

  identity {
    type = "SystemAssigned"
  }

  role_based_access_control {
    enabled = true
  }

  tags = {
    Vini = "ETL-AZURE-AKS"
  }

}