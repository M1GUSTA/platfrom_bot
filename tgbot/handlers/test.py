import re

import requests as requests


from tgbot.config import Config

def pop(config: Config):
    admins = config.tg_bot.admin_ids
    for admin in admins:
        requests.post(f"https://api.telegram.org/bot5309284298:AAEOrd2QDgAFjFtKzCkGhgG3Bi4luepnTjU/"
                  f"sendMessage?chat_id={admin}&text=Гусь петух")

pop(Config)