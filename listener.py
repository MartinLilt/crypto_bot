import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
BOT_USERNAME = os.getenv("BOT_USERNAME")
TG_SESSION = os.getenv("TG_SESSION")

client = TelegramClient(StringSession(TG_SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(chats=CHANNEL_ID))
async def handler(event):
    try:
        await client.forward_messages(BOT_USERNAME, event.message)
        print("✅ Сообщение переслано целиком")
    except Exception as e:
        print("❌ Ошибка при пересылке:", e)


async def main():
    print("🎧 Слушаю канал и пересылаю в бота...")

client.start()
client.loop.run_until_complete(main())
client.run_until_disconnected()
