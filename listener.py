from telethon import TelegramClient, events

api_id = 23960136
api_hash = "5ebee58f511d916fd634ff99ab20ac9d"

channel_id = -1001695131110
bot_username = "@AleksandLi"

client = TelegramClient("my_session", api_id, api_hash)

@client.on(events.NewMessage(chats=channel_id))
async def handler(event):
    try:
        await client.forward_messages(bot_username, event.message)
        print("✅ Сообщение переслано целиком")
    except Exception as e:
        print("❌ Ошибка при пересылке:", e)


async def main():
    print("🎧 Слушаю канал Market insight и пересылаю в бота...")

client.start()
client.loop.run_until_complete(main())
client.run_until_disconnected()
