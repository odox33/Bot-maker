import os
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_NAME = "Source TP"
BOT_USERNAME = "@odox6"
BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

app = Flask(__name__)
application = None

async def setup_bot():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    await application.initialize()
    if RENDER_URL:
        webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("• اضف البوت لمجموعتك •", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("• قناة السورس •", url="https://t.me/odox6")],
        [InlineKeyboardButton("• المطور •", url=f"tg://user?id={user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        f"مرحباً بك عزيزي في بوت {BOT_NAME} 🤖\n\n"
        f"• أسرع بوت حماية مجموعات مطور خصيصاً ليكون البديل الأقوى.\n"
        f"• اضف البوت إلى مجموعتك وارفعه مشرفاً لتبدأ الحماية فوراً!"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    text = (
        f"• مـعـلـومـاتـك الشخصية :\n\n"
        f"• الايدي : `{user.id}`\n"
        f"• المعرف : @{user.username if user.username else 'لا يوجد'}\n"
        f"• الاسم : {user.first_name}\n\n"
        f"• معلومات السورس : {BOT_NAME} ({BOT_USERNAME})\n"
        f"• ايدي الدردشة : `{chat.id}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("• إحصائيات Source TP •", callback_data="admin_stats")],
        [InlineKeyboardButton("• قسم الإذاعة •", callback_data="admin_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"أهلاً بك في لوحة تحكم {BOT_NAME} الأساسية ⚡️\nاختر أحد الخيارات أدناه:"
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "admin_stats":
        await query.edit_message_text(f"• حالة السورس: يعمل بوت {BOT_NAME} بكفاءة عالية وبدون أي مشاكل 🚀")
    elif query.data == "admin_broadcast":
        await query.edit_message_text("• أرسل النص أو الرسالة التي تريد إذاعتها للمستخدمين.")

@app.route('/')
def home():
    return "Source TP Webhook Server is running!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    import asyncio
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return 'ok', 200

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_bot())
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
