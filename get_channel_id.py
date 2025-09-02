import os, re, unicodedata
from telethon import TelegramClient, functions
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID", "23960136"))
API_HASH = os.getenv("API_HASH", "5ebee58f511d916fd634ff99ab20ac9d")
TG_SESSION_DEV = os.getenv("TG_SESSION_DEV")
QUERY = "crypto volk spot investment"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "")
    s = s.replace("\u00A0", " ")
    return re.sub(r"\s+", " ", s.strip()).lower()


client = TelegramClient(
    StringSession(TG_SESSION_DEV) 
    if TG_SESSION_DEV else "my_session_dev", API_ID, API_HASH)


async def find_in_folder(client, folder=None):
    hits = []
    async for d in client.iter_dialogs(folder=folder):
        if QUERY in norm(d.name):
            hits.append(d)
    return hits


async def main():
    await client.start()
    print("Ищу в диалогах (основная и Архив)...")
    hits = (await find_in_folder(client, 0)) + (await find_in_folder(client, 1))
    if hits:
        for d in hits:
            print(f"✅ {d.name!r} — id={d.id} — {d.entity.__class__.__name__}")
        return
    print("Делаю глобальный поиск…")
    res = await client(functions.contacts.SearchRequest(q=QUERY, limit=50))
    found = False

    for ch in res.chats:
        if QUERY in norm(ch.title):
            found = True; print(f"🔎 chat: {ch.title!r} — id={ch.id}")
    for u in res.users:
        full = f"{u.first_name or ''} {u.last_name or ''}".strip()
        if full and QUERY in norm(full):
            found = True; print(f"🔎 user: {full!r} — id={u.id}")
    if not found:
        print("❌ Не найдено. Проверь подписку/название/папки.")

with client:
    client.loop.run_until_complete(main())
