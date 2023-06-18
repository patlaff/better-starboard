variable "env" {
  type = string
}

variable "network" {
  type = object({
    address_space = string
    subnet_size   = number
  })
}