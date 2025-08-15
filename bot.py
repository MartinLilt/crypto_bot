import os
import requests
from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

analyze_coin = '📊 Анализ монеты'
find_coin = '🔍 Найти монету'
coin_labels = {
    "BTC": "BTC (Биткоин)",
    "ETH": "ETH (Эфириум)",
    "SOL": "SOL (Солана)",
    "DOGE": "DOGE (Догикоин)",
    "ADA": "ADA (Кардано)",
    "XRP": "XRP (Рипл)",
    "DOT": "DOT (Полкадот)",
    "AVAX": "AVAX (Аваланч)",
    "LTC": "LTC (Лайткоин)",
    "MATIC": "MATIC (Полигон)",
    "BNB": "BNB (Бинанс Коин)",
    "LINK": "LINK (Чейнлинк)"
}


def chunked_buttons(items, row_size=2):
    return [items[i:i + row_size] for i in range(0, len(items), row_size)]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[KeyboardButton(analyze_coin), KeyboardButton(find_coin)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Выберите опцию ниже:", reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == analyze_coin:

        coin_buttons = chunked_buttons(
            [KeyboardButton(label) for label in coin_labels.values()], 
            row_size=2
        )

        coin_buttons.append([KeyboardButton("🔙 Назад")])
        reply_markup = ReplyKeyboardMarkup(coin_buttons, resize_keyboard=True)
        await update.message.reply_text(
            "Выберите монету для анализа:", 
            reply_markup=reply_markup
        )

    elif text in coin_labels.values():
        symbol = next((k for k, v in coin_labels.items() if v == text), None)

        if symbol:

            info = get_binance_coin_analysis(symbol)
            keyboard = [[KeyboardButton("🔙 Назад")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text(
                info, 
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

        else:
            await update.message.reply_text("⚠️ Неизвестная монета.")

    elif text == find_coin:
        recommended = find_best_coins_to_buy(list(coin_labels.keys()), top_n=3)
        keyboard = [[KeyboardButton("🔙 Назад")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            recommended, reply_markup=reply_markup, parse_mode="Markdown"
        )

    elif text == "🔙 Назад":
        keyboard = [
            [KeyboardButton(analyze_coin), KeyboardButton(find_coin)]
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Возврат в главное меню 👇",
            reply_markup=reply_markup
        )

    else:
        await update.message.reply_text("Пожалуйста, используйте кнопки 🙃")


def get_binance_coin_analysis(symbol: str) -> str:
    pair = f"{symbol.upper()}USDT"
    url = "https://api.binance.com/api/v3/ticker/24hr"

    try:
        response = requests.get(url, params={"symbol": pair})
        data = response.json()

        if "code" in data:
            return f"❌ Монета {symbol} не найдена на Binance."

        price = float(data["lastPrice"])
        change = float(data["priceChangePercent"])
        volume = float(data["quoteVolume"])
        high = float(data["highPrice"])
        low = float(data["lowPrice"])
        trades = int(data["count"])

        if change > 2:
            trend = "Бычий 🟢"
        elif change < -2:
            trend = "Медвежий 🔻"
        else:
            trend = "Боковой 🔄"

        return (
            f"📊 Анализ {symbol.upper()}USDT\n\n"
            f"💵 Цена: `${price:,.2f}`\n"
            f"📉 Изменение за 24ч: `{change:.2f}%`\n"
            f"📈 Макс / Мин за 24ч: `${high:,.2f}` / `${low:,.2f}`\n"
            f"📊 Объём за 24ч: `${volume:,.0f}`\n"
            f"📍 Кол-во сделок: `{trades}`\n"
            f"📘 Текущий тренд: *{trend}*"
        )

    except Exception as e:
        return f"⚠️ Ошибка при получении данных: {e}"
    

def find_best_coins_to_buy(coin_list: list, top_n: int = 1) -> str:
    url = "https://api.binance.com/api/v3/ticker/24hr"
    best = []

    try:
        for symbol in coin_list:
            pair = f"{symbol}USDT"
            response = requests.get(url, params={"symbol": pair})
            data = response.json()

            if "code" in data:
                continue

            change = float(data["priceChangePercent"])
            volume = float(data["quoteVolume"])

            if volume > 5_000_000 and change > 0:
                best.append((symbol, change, volume))

        if not best:
            return "🤷 Не удалось найти монету для покупки прямо сейчас."

        best.sort(key=lambda x: x[1], reverse=True)
        top = best[:top_n]

        msg = "🟢 *Рекомендуемые монеты для покупки:*\n\n"
        for symbol, change, volume in top:
            name = coin_labels.get(symbol, symbol)
            msg += f"• {name}\n  Изменение: `{change:.2f}%`\n  Объём: `${volume:,.0f}`\n\n"

        return msg

    except Exception as e:
        return f"⚠️ Ошибка при анализе монет: {e}"


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
