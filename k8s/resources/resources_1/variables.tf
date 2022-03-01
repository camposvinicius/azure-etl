variable "storage_account_name" {
  default = "vinietlazure"
}

variable "resource_group_name" {
  default = "vinietlazure"
}

variable "location" {
  default = "East US"
}

variable "sqlserver_user" {
  default = "vinietlazure"
}

variable "sqlserver_pass" {
  default = "A1b2C3d4"
}

variable "containers_names" {
  type = list(string)
  default = [
    "bronze",
    "silver",
    "gold"
  ]
}