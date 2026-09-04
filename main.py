import os
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# إعداد السجلات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت الخاص بك
TOKEN = "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w"

# --- قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user(user_id, username, full_name):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, full_name) 
        VALUES (?, ?, ?)
    """, (user_id, username, full_name))
    conn.commit()
    conn.close()

# --- واجهة البوت والأساسيات ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username, user.full_name)
    
    # القائمة الرئيسية الواضحة والمقسمة
    keyboard = [
        [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
        [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
        [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
        [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"أهلاً بك يا {user.first_name} في منصة إدارة وصناعة البوتات.\n"
        "اختر أحد الخيارات أدناه للبدء:"
    )
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text=welcome_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=welcome_text, reply_markup=reply_markup)

# --- معالجة الأزرار التفاعلية ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "free_bot_maker":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="🛠 **قسم صانع البوتات المجاني:**\n\nهنا يمكنك إنشاء بوتات مجانية بالمميزات الأساسية المتاحة.\n(قريباً سيتم تفعيل الخدمة تلقائياً)",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    elif query.data == "paid_bot_maker":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="💎 **قسم صانع البوتات المدفوع:**\n\nيمنحك بوتات احترافية بدون رعاية، مع ميزات متقدمة ودعم فني خاص وحماية عالية.\nللاشتراك تواصل مع المطور.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    elif query.data == "dev_contact":
        keyboard = [
            [InlineKeyboardButton("💬 مراسلة المطور", url="https://t.me/your_username")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="👨‍💻 **معلومات المطور:**\n\nللدعم الفني، الاستفسارات، أو طلب الخدمات المدفوعة، يمكنك التواصل مع المطور مباشرة.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    elif query.data == "get_my_id":
        user = update.effective_user
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"🆔 الآيدي الخاص بك هو:\n`{user.id}`",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    elif query.data == "back_to_start":
        # العودة للقائمة الرئيسية بنفس الواجهة
        user = update.effective_user
        keyboard = [
            [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
            [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
            [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
            [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"أهلاً بك يا {user.first_name} مرة أخرى في القائمة الرئيسية:",
            reply_markup=reply_markup
        )

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"🆔 الآيدي الخاص بك هو:\n`{user.id}`", parse_mode="Markdown")

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    PORT = int(os.environ.get("PORT", "10000"))
    RENDER_URL = "https://bot-maker-1-709e.onrender.com"

    logger.info("Starting bot via Webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
