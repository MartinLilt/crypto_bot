import os, sys
from telethon import TelegramClient, events
from telethon.sessions import StringSession


def require_env(name, cast=str):
    v = os.getenv(name)
    if v is None or not str(v).strip():
        sys.exit(f"Missing required env var: {name}")
    try:
        return cast(v.strip()) if cast is int else cast(v)
    except Exception:
        sys.exit(f"Invalid value for {name}: {v!r}")


API_ID = require_env("API_ID", int)
API_HASH = require_env("API_HASH", str)
CHANNEL_ID = require_env("CHANNEL_ID", int)
BOT_USERNAME = require_env("BOT_USERNAME", str)
TG_SESSION = require_env("TG_SESSION", str)

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
