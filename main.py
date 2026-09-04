import os
import sqlite3
import logging
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_NAME = "Source TP"
BOT_USERNAME = "@odox6"
DEV_ID = 8297163405
BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

app = Flask(__name__)
application = None
loop = None

# قاعدة بيانات بسيطة لتفعيل القروبات
def init_db():
    conn = sqlite3.connect("source_tp.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS active_groups (chat_id INTEGER PRIMARY KEY, status TEXT)")
    conn.commit()
    conn.close()

init_db()

async def setup_bot():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_message_handler))
    
    await application.initialize()
    if RENDER_URL:
        webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
        await application.bot.set_webhook(url=webhook_url)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type != "private":
        return
    await update.message.reply_text(
        f"مرحباً بك في بوت {BOT_NAME} 🤖\n\nأضفني إلى مجموعتك واكتب **تفعيل** لتبدأ الحماية ويعمل أمر **ايدي** فوراً!"
    )

async def main_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    text = update.message.text.strip()
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. أمر التفعيل داخل المجموعة
    if text == "تفعيل":
        if chat.type == "private":
            await update.message.reply_text("• هذا الأمر يُستخدم داخل المجموعات فقط!")
            return
            
        conn = sqlite3.connect("source_tp.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO active_groups (chat_id, status) VALUES (?, ?)", (chat.id, "active"))
        conn.commit()
        conn.close()
        
        await update.message.reply_text("✅ **تم تفعيل البوت بنجاح!**\n\n• الآن يمكنك استخدام أمر ( ايدي ) أو ( طرد ) أو ( رفع مشرف ).", parse_mode="Markdown")
        return

    # التحقق هل المجموعة مفعلة لكي يستجيب البوت للأوامر داخلها
    if chat.type != "private":
        conn = sqlite3.connect("source_tp.db")
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM active_groups WHERE chat_id = ?", (chat.id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or result[0] != "active":
            return

    # 2. أمر الأيدي (بنفس تنسيق سورس ماريو الفخم)
    if text in ["ايدي", "الاي دي", "ايديي", "/id"]:
        id_text = (
            f"• - : ايديك : ( `{user.id}` )\n"
            f"• - : معرفك : ( @{user.username if user.username else 'لا يوجد'} )\n"
            f"• - : اسمك : ( {user.first_name} )\n"
            f"• - : ايدي القروب : ( `{chat.id}` )\n"
            f"• معلومات السورس : {BOT_NAME} ({BOT_USERNAME})"
        )
        await update.message.reply_text(id_text, parse_mode="Markdown")

    # 3. أمر طرد (بالرد على الرسالة)
    elif text == "طرد" and update.message.reply_to_message:
        try:
            target_user = update.message.reply_to_message.from_user
            await context.bot.ban_chat_member(chat.id, target_user.id)
            await update.message.reply_text(f"🔨 تم طرد العضو {target_user.first_name} بنجاح.")
        except Exception:
            await update.message.reply_text("⚠️ عذراً، لا أملك صلاحية الطرد أو أن الشخص مشرف.")

    # 4. أمر رفع مشرف (بالرد على الرسالة)
    elif text == "رفع مشرف" and update.message.reply_to_message:
        try:
            target_user = update.message.reply_to_message.from_user
            await context.bot.promote_chat_member(
                chat.id, target_user.id,
                can_manage_chat=True,
                can_delete_messages=True,
                can_invite_users=True
            )
            await update.message.reply_text(f"⭐ تم رفع العضو {target_user.first_name} مشرفاً بنجاح.")
        except Exception:
            await update.message.reply_text("⚠️ عذراً، لا أملك صلاحية رفع المشرفين.")

@app.route('/')
def home():
    return "Bot is running perfectly!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string, application.bot)
        future = asyncio.run_coroutine_threadsafe(application.process_update(update), loop)
        future.result()
        return 'ok', 200
    return 'invalid format', 403

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_bot())
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
