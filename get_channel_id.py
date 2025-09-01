from telethon import TelegramClient, functions
import re
import unicodedata

api_id = 23960136
api_hash = "5ebee58f511d916fd634ff99ab20ac9d"
QUERY = "crypto volk spot investment"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "")
    s = s.replace("\u00A0", " ")
    s = re.sub(r"\s+", " ", s.strip()).lower()
    return s


async def find_in_folder(client, folder=None):
    hits = []
    async for d in client.iter_dialogs(folder=folder):
        name_n = norm(d.name)
        if QUERY in name_n:
            hits.append(d)
    return hits


async def main():
    await client.start()

    print("Ищу в диалогах (основная вкладка и Архив)...")
    hits_main = await find_in_folder(client, folder=0)   # основная
    hits_arch = await find_in_folder(client, folder=1)   # архив

    hits = hits_main + hits_arch
    if hits:
        for d in hits:
            ent = d.entity
            print("✅ Найдено в диалогах:")
            print(f"Название: {d.name!r}")
            print(f"ID: {d.id}")
            print(f"Тип: {ent.__class__.__name__}")
        return

    print("В диалогах не нашли. Делаю глобальный поиск...")
    res = await client(functions.contacts.SearchRequest(q=QUERY, limit=50))
    candidates = []
    for ch in res.chats:
        candidates.append(("chat", ch.id, ch.title))
    for u in res.users:
        full = f"{u.first_name or ''} {u.last_name or ''}".strip()
        if full:
            candidates.append(("user", u.id, full))

    found_any = False
    for typ, _id, title in candidates:
        if QUERY in norm(title):
            found_any = True
            print(f"🔎 Похоже на совпадение ({typ}): {title!r} — id={_id}")

    if not found_any:
        print("❌ Не найдено. Проверь:")
        print("1) Ты точно подписан на канал этим аккаунтом (той же сессией)?")
        print("2) Канал не скрыт в другом аккаунте/папке?")
        print("3) У канала может быть другое реальное имя/эмодзи/лишние пробелы.")
        print("   Скопируй точное название из Telegram и подставь в QUERY.")

client = TelegramClient("my_session", api_id, api_hash)
with client:
    client.loop.run_until_complete(main())
