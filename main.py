import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# أمر الترحيب وحماية المجموعات
async def protect_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            await update.message.reply_text(
                f"أهلاً بك {member.first_name} في البوت! تم تفعيل الحماية بنجاح."
            )

def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("لم يتم العثور على متغير البيئة BOT_TOKEN!")
        return

    application = ApplicationBuilder().token(token).build()

    # مراقبة دخول الأعضاء الجدد لحمايتهم
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, protect_group))

    logger.info("تم تشغيل البوت بنجاح...")
    application.run_polling()

if __name__ == "__main__":
    main()
