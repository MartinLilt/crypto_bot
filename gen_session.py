from telethon import TelegramClient
from telethon.sessions import StringSession

api_id = 23960136
api_hash = "5ebee58f511d916fd634ff99ab20ac9d"

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print(client.session.save())
