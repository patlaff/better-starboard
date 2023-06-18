env="prd"

network = {
    address_space = "10.0.0.0/16"
    subnet_size = 21
}

# containers = {
#     foundryvtt = {
#         image = "felddy/foundryvtt:9.242"
#         cpu = "0.25"
#         memory = "0.5Gi"
#         port = 30000
#         args = {
#             cap_add = "sys_nice"
#         }
#         secret_env = {
#             FOUNDRY_ADMIN_KEY = "foundry-admin-key"
#             FOUNDRY_PASSWORD = "foundry-password"
#             FOUNDRY_USERNAME = "foundry-username"
#             FOUNDRY_LICENSE_KEY = "foundry-license-key"
#         }
#         env = {
#             FOUNDRY_UID = "1000"
#             FOUNDRY_GID = "1002"
#         }
#         volumes = {
#             "foundryvtt-data" = {
#                 size_in_gb = 50
#                 access_mode = "ReadWrite"
#                 mount_path = "/data"
#             }
#         }
#     }
#     valheim = {
#         image = "lloesche/valheim-server"
#         cpu = "0.25"
#         memory = "0.5Gi"
#         port = 2456-2458
#         args = {
#             cap_add = "sys_nice"
#         }
#         secret_env = {
#         }
#         env = {
#             SERVER_NAME = "wenchland"
#             WORLD_NAME = "Wenchland"
#             SERVER_PASS = "test"
#             SERVER_PUBLIC = false
#         }
#         volumes = {
#             "valheim-config" = {
#                 size_in_gb = 50
#                 access_mode = "ReadWrite"
#                 mount_path = "/config"
#             }
#             "data" = {
#                 size_in_gb = 50
#                 access_mode = "ReadWrite"
#                 mount_path = "/opt/valheim"
#             }
#         }
#     }
# }