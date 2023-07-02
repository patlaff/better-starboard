variable "env" {
  type = string
}

variable "network" {
  type = object({
    address_space = string
    subnet_size   = number
  })
}

variable "image_tag" {
  type = string
  default = "latest"
}