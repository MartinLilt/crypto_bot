from telethon import TelegramClient

api_id = 23960136
api_hash = "5ebee58f511d916fd634ff99ab20ac9d"

client = TelegramClient("my_session", api_id, api_hash)


async def main():
    print("Поиск канала 'Market insight'...\n")
    async for dialog in client.iter_dialogs():
        if 'Market insight' in dialog.name:
            print("✅ Найден канал:")
            print(f"Название: {dialog.name}")
            print(f"ID: {dialog.id}")
            print(f"Тип: {dialog.entity.__class__.__name__}")
            return
    print("❌ Канал не найден. Убедись, что ты подписан на него.")

with client:
    client.loop.run_until_complete(main())
