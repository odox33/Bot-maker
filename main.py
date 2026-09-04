import os
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# إعداد السجلات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت والمعرفات الخاصة بك
TOKEN = "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w"
DEV_USERNAME = "odox3"  # معرف المطور بدون @
CHANNEL_USERNAME = "@odox6"  # قناة السورس للاشتراك الإجباري

# --- قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    # جدول المستخدمين
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT
        )
    """)
    # جدول إعدادات البوت (مثل الاشتراك الإجباري: مفعل/معطل)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    # وضع القيمة الافتراضية للاشتراك الإجباري (مفعل: active)
    cursor.execute("""
        INSERT OR IGNORE INTO settings (key, value) VALUES ('forced_sub', 'active')
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

def get_setting(key):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "active"

def set_setting(key, value):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
    conn.commit()
    conn.close()

# دالة التحقق من اشتراك المستخدم في القناة
async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        # إذا كان عضو، كاتب، أو أدمن تعتبر الحالة مقبولة
        if member.status in ["member", "creator", "administrator"]:
            return True
    except TelegramError:
        pass
    return False

# --- الواجهة الرئيسية ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username, user.full_name)
    
    keyboard = [
        [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
        [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
        [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
        [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
    ]
    
    # إضافة زر إعدادات البوت تلقائياً إذا كان المستخدم هو المطور
    if user.username and user.username.lower() == DEV_USERNAME.lower():
        keyboard.insert(0, [InlineKeyboardButton("⚙️ إعدادات البوت والتحكم", callback_data="admin_settings")])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = f"أهلاً بك يا {user.first_name} في منصة إدارة وصناعة البوتات.\nاختر أحد الخيارات أدناه للبدء:"
    
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text=welcome_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=welcome_text, reply_markup=reply_markup)

# --- معالجة الأزرار ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    await query.answer()
    
    if query.data == "free_bot_maker":
        # التحقق من حالة الاشتراك الإجباري من القاعدة
        forced_status = get_setting("forced_sub")
        
        if forced_status == "active":
            is_subscribed = await check_subscription(user.id, context.bot)
            if not is_subscribed:
                # إذا لم يكن مشتركاً، نطلب منه الاشتراك مع زر التحقق
                keyboard = [
                    [InlineKeyboardButton("📢 اشترك في قناة السورس", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
                    [InlineKeyboardButton("✅ لقد اشتريت / تحققت", callback_data="free_bot_maker")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
                ]
                await query.edit_message_text(
                    text=f"⚠️ **عذراً، يجب عليك الاشتراك في قناة البوت أولاً لتسخدم صانع البوتات المجاني.**\n\nالقناة: {CHANNEL_USERNAME}\n\nبعد الاشتراك اضغط على زر التحقق أسفله:",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                return

        # إذا كان مشترك أو الاشتراك معطل، ندخله للقسم
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(
            text="🛠 **قسم صانع البوتات المجاني:**\n\nأهلاً بك! يمكنك الآن البدء بصنع بوتك المجاني بكل سهولة.\n(أرسل تفاصيل بوتك أو انتظر تفعيل الخدمات التلقائية)",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
    elif query.data == "paid_bot_maker":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(
            text="💎 **قسم صانع البوتات المدفوع:**\n\nيمنحك بوتات احترافية بدون رعاية، مع ميزات متقدمة ودعم فني خاص وحماية عالية.\nللاشتراك تواصل مع المطور مباشرة.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
    elif query.data == "dev_contact":
        keyboard = [
            [InlineKeyboardButton("💬 مراسلة المطور", url=f"https://t.me/{DEV_USERNAME}")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
        ]
        await query.edit_message_text(
            text=f"👨‍💻 **معلومات المطور:**\n\nللدعم الفني والاستفسارات:\nالمطور: @{DEV_USERNAME}\nقناة السورس: {CHANNEL_USERNAME}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
    elif query.data == "get_my_id":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(
            text=f"🆔 الآيدي الخاص بك هو:\n`{user.id}`",
            reply_markup=keyboard_to_markup(keyboard),
            parse_mode="Markdown"
        )
        
    elif query.data == "admin_settings":
        # لوحة تحكم المطور
        if user.username and user.username.lower() == DEV_USERNAME.lower():
            current_status = get_setting("forced_sub")
            status_text = "🟢 مفعل" if current_status == "active" else "🔴 معطل"
            toggle_action = "disable_forced" if current_status == "active" else "enable_forced"
            toggle_label = "إيقاف الاشتراك الإجباري" if current_status == "active" else "تفعيل الاشتراك الإجباري"
            
            keyboard = [
                [InlineKeyboardButton(f"الاشتراك الإجباري: {status_text}", callback_data=toggle_action)],
                [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
            ]
            await query.edit_message_text(
                text="⚙️ **لوحة تحكم إعدادات البوت:**\n\nمن هنا يمكنك التحكم بخواص البوت والاشتراك الإجباري:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await query.answer("هذا القسم مخصص للمطور فقط!", show_alert=True)
            
    elif query.data in ["enable_forced", "disable_forced"]:
        if user.username and user.username.lower() == DEV_USERNAME.lower():
            new_val = "active" if query.data == "enable_forced" else "disabled"
            set_setting("forced_sub", new_val)
            # إعادة توجيه لنفس صفحة الإعدادات لتحديث الزر
            current_status = "🟢 مفعل" if new_val == "active" else "🔴 معطل"
            toggle_action = "disable_forced" if new_val == "active" else "enable_forced"
            toggle_label = "إيقاف الاشتراك الإجباري" if new_val == "active" else "تفعيل الاشتراك الإجباري"
            
            keyboard = [
                [InlineKeyboardButton(f"الاشتراك الإجباري: {current_status}", callback_data=toggle_action)],
                [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
            ]
            await query.edit_message_text(
                text="⚙️ **تم تحديث الإعدادات بنجاح!**\n\nلوحة تحكم إعدادات البوت:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            
    elif query.data == "back_to_start":
        # العودة للقائمة الرئيسية
        keyboard = [
            [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
            [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
            [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
            [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
        ]
        if user.username and user.username.lower() == DEV_USERNAME.lower():
            keyboard.insert(0, [InlineKeyboardButton("⚙️ إعدادات البوت والتحكم", callback_data="admin_settings")])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=f"أهلاً بك يا {user.first_name} مرة أخرى في القائمة الرئيسية:",
            reply_markup=reply_markup
        )

# مساعدة للأزرار البسيطة
def keyboard_to_markup(kb):
    return InlineKeyboardMarkup(kb)

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
