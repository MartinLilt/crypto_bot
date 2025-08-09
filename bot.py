import os
import json
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

MAIN_KB = ReplyKeyboardMarkup(
    [["📈 Сигналы", "📜 История"], ["📊 Статистика", "💬 Поддержка"]],
    resize_keyboard=True
)

def buy_signal() -> str:
    entry = 122.30
    t1, t2, t3 = 125.00, 127.40, 130.80
    return (
        f"🟢 BUY: #LTCUSDT (Spot)\n\n"
        f"📊 Вход: {entry:.2f} (±0.3%)\n"
        f"⛔ Инвалидация: Close < MA50(D1) или -1.5×ATR\n"
        f"🎯 Цели:\n"
        f"  • T1: {t1:.2f} (+{(t1/entry-1)*100:.1f}%)\n"
        f"  • T2: {t2:.2f} (+{(t2/entry-1)*100:.1f}%)\n"
        f"  • T3: {t3:.2f} (+{(t3/entry-1)*100:.1f}%)\n\n"
        f"🔎 Причины: onchain_netflow_negative, sentiment_positive, macd_hist_positive_4h\n"
        f"📈 Доля: до 35% портфеля, риск 1%\n\n"
        f"⚠️ Это не инвестсовет."
    )

def trim_signal() -> str:
    return (
        f"🎯 Фиксация прибыли (TRIM 50%)\n"
        f"✅ #LTCUSDT (Spot)\n"
        f"📊 Цена: 125.00 — закрыть 50% позиции\n"
        f"ℹ️ Причина: достигнута цель T1"
    )

def cancel_signal() -> str:
    return (
        f"⛔ Отмена сценария\n"
        f"#LTCUSDT (Spot)\n"
        f"📊 Цена: 119.50 — пробита инвалидация\n\n"
        f"🧭 Действие: закрыть позицию, ждать нового сигнала."
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Привет! Я — Crypto Signals Bot 💡\n"
        "Даю сигналы для спотовой торговли с входом, целями и инвалидацией.\n\n"
        "🚀 Нажми «📈 Сигналы», чтобы увидеть пример."
    )
    await update.message.reply_text(text, reply_markup=MAIN_KB)

async def signals_demo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📉 График", callback_data="chart"),
         InlineKeyboardButton("ℹ Объяснение", callback_data="explain")]
    ])
    await update.message.reply_text(buy_signal(), reply_markup=kb, parse_mode=ParseMode.MARKDOWN)

async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "explain":
        explanation = {
            "symbol": "LTCUSDT",
            "score": 0.58,
            "confidence": 0.79,
            "drivers": ["onchain_netflow_negative", "sentiment_positive", "macd_hist_positive_4h"],
            "entry": 122.3,
            "targets": [125.0, 127.4, 130.8],
            "invalidation": "Close < MA50(D1) или -1.5×ATR",
            "position_size": 0.35,
            "risk": 0.01
        }
        await q.message.reply_text(f"```json\n{json.dumps(explanation, indent=2, ensure_ascii=False)}\n```", parse_mode=ParseMode.MARKDOWN_V2)
    elif q.data == "chart":
        await q.message.reply_text("📉 График: (тут можно будет прислать картинку или ссылку)")

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (update.message.text or "").strip()
    if txt == "📈 Сигналы":
        return await signals_demo(update, context)
    if txt == "📜 История":
        return await update.message.reply_text("1) BUY LTC @122.3 → TP2\n2) CANCEL BTCUSDT (-0.5%)")
    if txt == "📊 Статистика":
        return await update.message.reply_text("WinRate: 78% · PF: 1.42 · MaxDD: 12%")
    if txt == "💬 Поддержка":
        return await update.message.reply_text("Поддержка: @your_support")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.run_polling()

if __name__ == "__main__":
    main()
