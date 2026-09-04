import os
import sqlite3
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_NAME = "Source TP"
BOT_USERNAME = "@odox6"
DEV_ID = 8297163405  # ايدي المطور الأساسي
BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

app = Flask(__name__)
application = None

# إعداد قاعدة البيانات للمجموعات المفعلة والبوتات المصنوعة
def init_db():
    conn = sqlite3.connect("source_tp.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS active_groups (
            chat_id INTEGER PRIMARY KEY,
            added_by INTEGER,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

async def setup_bot():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_text_handler))
    
    await application.initialize()
    if RENDER_URL:
        webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type != "private":
        return  # إذا كان في مجموعة يتجاهل الـ start
        
    keyboard = [
        [InlineKeyboardButton("• اضف البوت لمجموعتك •", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("• قناة السورس •", url="https://t.me/odox6")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        f"مرحباً بك عزيزي في بوت {BOT_NAME} 🤖\n\n"
        f"• أسرع بوت حماية مجموعات متطور.\n"
        f"• أضف البوت إلى مجموعتك واكتب **تفعيل** لتبدأ الحماية وإدارة القروب فوراً!"
    )
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    text = (
        f"• - : ايديك : ( `{user.id}` )\n"
        f"• - : معرفك : ( @{user.username if user.username else 'لا يوجد'} )\n"
        f"• - : اسمك : ( {user.first_name} )\n"
        f"• - : ايدي القروب : ( `{chat.id}` )\n"
        f"• معلومات السورس : {BOT_NAME} ({BOT_USERNAME})"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def group_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    text = update.message.text.strip()
    chat = update.effective_chat
    user = update.effective_user
    
    # 1. أمر التفعيل داخل المجموعة
    if text == "تفعيل":
        if chat.type == "private":
            await update.message.reply_text("• هذا الأمر يُستخدم داخل المجموعات فقط لتفعيل البوت!")
            return
            
        conn = sqlite3.connect("source_tp.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO active_groups (chat_id, added_by, status) VALUES (?, ?, ?)",
                       (chat.id, user.id, "active"))
        conn.commit()
        conn.close()
        
        keyboard = [
            [InlineKeyboardButton("• قناة السورس •", url="https://t.me/odox6")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"✅ **تم تفعيل البوت بنجاح في المجموعة!**\n\n"
            f"• بواسطة العضو: {user.first_name}\n"
            f"• تم تفعيل نظام الحماية، الأيدي، البحث، وأوامر الإدارة بالكامل عبر {BOT_NAME}.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return

    # التحقق هل المجموعة مفعلة لكي تستجيب للأوامر
    if chat.type != "private":
        conn = sqlite3.connect("source_tp.db")
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM active_groups WHERE chat_id = ?", (chat.id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or result[0] != "active":
            # إذا لم يتم كتابة تفعيل، لا يستجيب القروب للأوامر
            return

    # 2. أمر الأيدي داخل القروب
    if text in ["ايدي", "الاي دي", "/id", "ايديي"]:
        await id_command(update, context)

    # 3. أمر البحث باليوتيوب (مثال: بحث أو يوتيوب [كلمة البحث])
    elif text.startswith("بحث ") or text.startswith("يوتيوب "):
        query_text = text.replace("بحث ", "", 1).replace("يوتيوب ", "", 1).strip()
        yt_url = f"https://www.youtube.com/results?search_query={query_text.replace(' ', '+')}"
        keyboard = [[InlineKeyboardButton("• اضغط لمشاهدة نتائج البحث •", url=yt_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"🔍 نتائج البحث في اليوتيوب عن: `{query_text}`", reply_markup=reply_markup, parse_mode="Markdown")

    # 4. أوامر الإدارة والحماية (طرد، كتم، رفع مشرف)
    elif text == "طرد" and update.message.reply_to_message:
        try:
            target_user = update.message.reply_to_message.from_user
            await context.bot.ban_chat_member(chat.id, target_user.id)
            await update.message.reply_text(f"🔨 تم طرد العضو {target_user.first_name} بنجاح.")
        except Exception:
            await update.message.reply_text("⚠️ عذراً، لا أملك صلاحية الطرد أو أن العضو مشرف.")

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

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != DEV_ID:
        return
    await update.message.reply_text(f"⚡️ أهلاً بك يا مطور {BOT_NAME} الأساسي في لوحة التحكم الخاصة.")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

@app.route('/')
def home():
    return "Source TP Group Bot Server is running!"

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
