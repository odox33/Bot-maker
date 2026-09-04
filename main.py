import os
import logging
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات لمتابعة حالة البوت
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# استبدل هذا التوكن بتوكن بوتك الحقيقي
TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"

def main():
    # بناء تطبيق البوت باستخدام التوكن
    application = Application.builder().token(TOKEN).build()

    # --- (أضف الهاندلرز والأوامر الخاصة بك هنا كما كانت في كودك الأصلي) ---
    # مثال: application.add_handler(CommandHandler("start", start))

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
