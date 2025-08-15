import os
import requests

from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          MessageHandler, filters)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
reserved_coins = [
    "BTC", "ETH", "SOL", "DOGE", 
    "ADA", "XRP", "DOT", "AVAX", 
    "LTC", "MATIC", "BNB", "LINK"
]


def chunked_buttons(items, row_size=2):
    return [items[i:i+row_size] for i in range(0, len(items), row_size)]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[KeyboardButton("Analyze coin"), KeyboardButton("Find coin")]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome! Choose an option below:", reply_markup=reply_markup
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Analyze coin":
        coin_buttons = chunked_buttons(
            [KeyboardButton(coin) for coin in reserved_coins], row_size=2
        )

        coin_buttons.append([KeyboardButton("🔙 Back")])
        reply_markup = ReplyKeyboardMarkup(coin_buttons, resize_keyboard=True)

        await update.message.reply_text(
            "Choose a coin to analyze:", reply_markup=reply_markup
        )

    elif text in reserved_coins:
        info = get_binance_coin_info(text)

        keyboard = [[KeyboardButton("🔙 Back")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            info, reply_markup=reply_markup, parse_mode="Markdown"
        )

    elif text == "Find coin":
        await update.message.reply_text("This feature is coming soon 🔍")

    elif text == "🔙 Back":
        keyboard = [
            [KeyboardButton("Analyze coin"), KeyboardButton("Find coin")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "Back to main menu 👇", reply_markup=reply_markup
        )

    else:
        await update.message.reply_text("Please use the buttons 🙃")


def get_binance_coin_info(symbol: str) -> str:
    pair = f"{symbol.upper()}USDT"

    try:
        response = requests.get(
            "https://api.binance.com/api/v3/ticker/24hr", 
            params={"symbol": pair}
        )
        data = response.json()

        if "code" in data:
            return f"❌ Coin {symbol} not found on Binance."

        price = float(data["lastPrice"])
        change = float(data["priceChangePercent"])
        volume = float(data["quoteVolume"])

        return (
            f"📈 *{symbol}USDT*\n"
            f"Price: `${price:,.2f}`\n"
            f"24h Change: `{change:.2f}%`\n"
            f"24h Volume: `${volume:,.0f}`"
        )

    except Exception as e:
        return f"⚠️ Error fetching data: {e}"


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
