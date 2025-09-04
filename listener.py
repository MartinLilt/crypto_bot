import os, sys, json
from pathlib import Path
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
TG_SESSION = require_env("TG_SESSION", str)

users = [os.getenv("BOT_USERNAME_1"), os.getenv("BOT_USERNAME_2")]
BOT_USERS = [u.strip() for u in users if u and u.strip()]
if not BOT_USERS:
    sys.exit("Missing required env var: BOT_USERNAME_1 or BOT_USERNAME_2")

client = TelegramClient(StringSession(TG_SESSION), API_ID, API_HASH)
MAP_PATH = Path("fwd_map.json")


def load_map():
    if MAP_PATH.exists():
        try:
            return json.loads(MAP_PATH.read_text())
        except Exception:
            return {}
    return {}


def save_map(m): MAP_PATH.write_text(json.dumps(m))


fwd_map = load_map()


def key_for(user, event):
    return f"{user}:{event.chat_id}:{event.message.id}"


async def forward_and_remember(event):
    """Переслать сообщение и запомнить связь оригинал→пересланное"""
    sent = []
    for user in BOT_USERS:
        fwd = await client.forward_messages(user, event.message)
        fwd_msg = fwd[0] if isinstance(fwd, (list, tuple)) else fwd
        fwd_map[key_for(user, event)] = fwd_msg.id
        sent.append(f"{user}:{fwd_msg.id}")
    save_map(fwd_map)
    print(f"✅ Переслано #{event.message.id} → " + ", ".join(sent))


@client.on(events.NewMessage(chats=CHANNEL_ID))
async def on_new(event):
    try:
        await forward_and_remember(event)
    except Exception as e:
        print("❌ Ошибка при первичной пересылке:", e)


@client.on(events.MessageEdited(chats=CHANNEL_ID))
async def on_edit(event):
    """Когда пост в канале отредактировали — обновляем у получателя"""
    id = event.message.id
    try:
        for user in BOT_USERS:
            k = key_for(user, event)
            fwd_id = fwd_map.get(k)
            if fwd_id:
                await client.delete_messages(user, fwd_id)
                fwd = await client.forward_messages(user, event.message)
                fwd_msg = fwd[0] if isinstance(fwd, (list, tuple)) else fwd
                fwd_map[k] = fwd_msg.id
                print(f"✏️ Обновлено сообщение #{id} для {user}")
            else:
                await forward_and_remember(event)
                print(f"ℹ️ Не нашли связь для #{id}, переслали заново")
        save_map(fwd_map)
    except Exception as e:
        try:
            for user in BOT_USERS:
                k = key_for(user, event)
                fwd_id = fwd_map.get(k)
                if fwd_id:
                    await client.edit_message(
                        user, fwd_id, event.message.message
                    )
                    
                    print(f"✏️ Отредактировали текст #{id} для {user}")
                else:
                    raise e
        except Exception as e2:
            print("❌ Ошибка при обновлении отредактированного поста:", e2)


async def main():
    print("🎧 Слушаю канал и пересылаю (учитывая правки)...")


client.start()
client.loop.run_until_complete(main())
client.run_until_disconnected()
