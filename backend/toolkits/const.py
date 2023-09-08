from apps.secret import models

WHITELIST_RIGHTS: tuple = ("can_write", "can_share", "can_export", "can_share_external")

MAPPING_SECRET: dict = {
    "login": models.Login,
    "server": models.Server,
    "phone": models.Phone,
    "bank": models.Bank,
}
