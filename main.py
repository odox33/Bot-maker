import os
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# إعداد السجلات لمتابعة حالة البوت
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت الخاص بك
TOKEN = "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w"

# دالة بداية التشغيل وإرسال الأزرار الشفافة الجديدة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("زر شفاف 1", callback_data="btn_1")],
        [InlineKeyboardButton("زر شفاف 2", callback_data="btn_2")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("أهلاً بك في الواجهة الجديدة:", reply_markup=reply_markup)

# دالة الاستجابة عند الضغط على الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"تم الضغط على: {query.data}")

def main():
    # بناء تطبيق البوت باستخدام التوكن
    application = Application.builder().token(TOKEN).build()

    # إضافة المعالجات (Handlers) للأوامر والأزرار
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    # الحصول على المنفذ (Port) المخصص من منصة رندر أو استخدام 10000 افتراضياً
    PORT = int(os.environ.get("PORT", "10000"))
    
    # رابط خدمتك الثابت على رندر
    RENDER_URL = "https://bot-maker-1-709e.onrender.com"

    logger.info("Starting bot via Webhook...")

    # تشغيل البوت باستخدام نظام الويب هوك لتجنب تعارض getUpdates نهائياً
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
