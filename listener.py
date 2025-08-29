from telethon import TelegramClient, events

api_id = 23960136
api_hash = "5ebee58f511d916fd634ff99ab20ac9d"

channel_id = -1001695131110
bot_username = "@CryptoAlexandrBot"

client = TelegramClient("my_session", api_id, api_hash)

@client.on(events.NewMessage(chats=channel_id))
async def handler(event):
    message = event.message.text

    print(f"🔄 Пересылаю сообщение в бота: {message}")
    try:
        await client.send_message(bot_username, message)
        print("✅ Успешно отправлено боту")
    except Exception as e:
        print("❌ Ошибка:", e)


async def main():
    print("🎧 Слушаю канал Market insight и пересылаю в бота...")

client.start()
client.loop.run_until_complete(main())
client.run_until_disconnected()
