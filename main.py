import os
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w"
DEV_USERNAME = "odox3"  # معرف المطور الأساسي
CHANNEL_USERNAME = "@odox6"  # قناة السورس

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
    
    # جدول الإعدادات العامة (الاشتراك الإجباري وحالة البوتات المدفوعة والمجانية)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('forced_sub', 'active')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('paid_bots_active', 'active')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('free_bots_active', 'active')")

    # جدول رتب المستخدمين (مميز، أدمن، مطور أساسي)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            user_id INTEGER PRIMARY KEY,
            role TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def save_user(user_id, username, full_name):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)", (user_id, username, full_name))
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

def get_user_role(user_id, username):
    if username and username.lower() == DEV_USERNAME.lower():
        return "owner"
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM roles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "user"

def set_user_role(user_id, role):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO roles (user_id, role) VALUES (?, ?)", (user_id, role))
    conn.commit()
    conn.close()

async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["member", "creator", "administrator"]:
            return True
    except TelegramError:
        pass
    return False

# --- الواجهة الرئيسية ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id, user.username, user.full_name)
    role = get_user_role(user.id, user.username)
    
    keyboard = [
        [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
        [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
        [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
        [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
    ]
    
    # لوحة المطور الأساسي أو الأدمن
    if role in ["owner", "admin", "dev"]:
        keyboard.insert(0, [InlineKeyboardButton("⚙️ إعدادات البوت والتحكم الأساسي", callback_data="admin_settings")])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = f"أهلاً بك يا {user.first_name} في منصة صناعة وإدارة البوتات الرئيسية."
    
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
    role = get_user_role(user.id, user.username)
    await query.answer()
    
    if query.data == "free_bot_maker":
        free_status = get_setting("free_bots_active")
        if free_status != "active":
            await query.answer("قسم صانع البوتات المجاني متوقف حالياً من قبل الإدارة.", show_alert=True)
            return

        forced_status = get_setting("forced_sub")
        if forced_status == "active":
            is_subscribed = await check_subscription(user.id, context.bot)
            if not is_subscribed:
                keyboard = [
                    [InlineKeyboardButton("📢 اشترك في قناة السورس", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
                    [InlineKeyboardButton("✅ لقد اشتريت / تحققت", callback_data="free_bot_maker")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
                ]
                await query.edit_message_text(
                    text=f"⚠️ **عذراً، يجب عليك الاشتراك في قناة السورس أولاً لاستخدام صانع البوتات المجاني.**\n\nالقناة: {CHANNEL_USERNAME}",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                return

        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(
            text="🛠 **قسم صانع البوتات المجاني:**\n\nأرسل توكن بوتك الجديد أو انقر على التعليمات للبدء بصنع بوتك المجاني بكل سهولة.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
    elif query.data == "paid_bot_maker":
        paid_status = get_setting("paid_bots_active")
        # البوتات المدفوعة تعمل منفصلة وبدون اشتراك إجباري
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        
        status_msg = "💎 **قسم صانع البوتات المدفوع:**\n\nبوتات احترافية بدون رعاية وبدون اشتراك إجباري!\nللاشتراك وتفعيل بوتك المدفوع، تواصل مع المطور."
        if role != "owner" and paid_status != "active":
            status_msg = "⚠️ قسم صانع البوتات المدفوعة متوقف مؤقتاً."

        await query.edit_message_text(
            text=status_msg,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
    elif query.data == "dev_contact":
        keyboard = [
            [InlineKeyboardButton("💬 مراسلة المطور", url=f"https://t.me/{DEV_USERNAME}")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
        ]
        await query.edit_message_text(
            text=f"👨‍💻 **معلومات المطور:**\nللدعم الفني:\nالمطور: @{DEV_USERNAME}\nالقناة: {CHANNEL_USERNAME}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
    elif query.data == "get_my_id":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(
            text=f"🆔 الآيدي الخاص بك هو:\n`{user.id}`",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        
    elif query.data == "admin_settings":
        if role in ["owner", "admin", "dev"]:
            f_sub = "🟢 مفعل" if get_setting("forced_sub") == "active" else "🔴 معطل"
            p_bots = "🟢 مفعل" if get_setting("paid_bots_active") == "active" else "🔴 معطل"
            
            keyboard = [
                [InlineKeyboardButton(f"الاشتراك الإجباري: {f_sub}", callback_data="toggle_forced")],
                [InlineKeyboardButton(f"البوتات المدفوعة: {p_bots}", callback_data="toggle_paid")],
                [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
            ]
            await query.edit_message_text(
                text="⚙️ **لوحة إعدادات البوت والتحكم:**",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await query.answer("مخصص للمطورين والأدمنية فقط!", show_alert=True)

    elif query.data in ["toggle_forced", "toggle_paid"]:
        if role == "owner": # التحكم الحصري للمطور الأساسي
            if query.data == "toggle_forced":
                curr = get_setting("forced_sub")
                set_setting("forced_sub", "disabled" if curr == "active" else "active")
            else:
                curr = get_setting("paid_bots_active")
                set_setting("paid_bots_active", "disabled" if curr == "active" else "active")
            
            # إعادة عرض اللوحة المحدثة
            f_sub = "🟢 مفعل" if get_setting("forced_sub") == "active" else "🔴 معطل"
            p_bots = "🟢 مفعل" if get_setting("paid_bots_active") == "active" else "🔴 معطل"
            keyboard = [
                [InlineKeyboardButton(f"الاشتراك الإجباري: {f_sub}", callback_data="toggle_forced")],
                [InlineKeyboardButton(f"البوتات المدفوعة: {p_bots}", callback_data="toggle_paid")],
                [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
            ]
            await query.edit_message_text(text="⚙️ **تم تحديث الإعدادات بنجاح:**", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.answer("هذا الخيار مخصص للمطور الأساسي فقط!", show_alert=True)

    elif query.data == "back_to_start":
        keyboard = [
            [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
            [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
            [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
            [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
        ]
        if role in ["owner", "admin", "dev"]:
            keyboard.insert(0, [InlineKeyboardButton("⚙️ إعدادات البوت والتحكم الأساسي", callback_data="admin_settings")])
            
        await query.edit_message_text(text="القائمة الرئيسية:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- أوامر الإدارة والمجموعات (رفع مميز، أدمن، مطور، كتم، طرد) ---
async def admin_commands_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return
    
    chat = message.chat
    if chat.type not in ["group", "supergroup"]:
        return

    user = message.from_user
    role = get_user_role(user.id, user.username)
    text = message.text

    # التحقق من الرد على رسالة لتنفيذ الأمر
    reply = message.reply_to_message
    target_user = reply.from_user if reply else None

    # أوامر الرفع والتنزيل (للمطور الأساسي والأدمن)
    if text.startswith("رفع مطور أساسي") and role == "owner":
        if target_user:
            set_user_role(target_user.id, "dev")
            await message.reply_text(f"👤 تم رفعه (مطور أساسي بنجاح: {target_user.first_name})")
    elif text.startswith("رفع أدمن") and role in ["owner", "dev"]:
        if target_user:
            set_user_role(target_user.id, "admin")
            await message.reply_text(f"👤 تم رفعه (أدمن بنجاح: {target_user.first_name})")
    elif text.startswith("رفع مميز") and role in ["owner", "dev", "admin"]:
        if target_user:
            set_user_role(target_user.id, "vip")
            await message.reply_text(f"⭐ تم رفعه (عضو مميز بنجاح: {target_user.first_name})")
            
    # أوامر الكتم والطرد في المجموعة
    elif text.startswith("طرد") and role in ["owner", "dev", "admin"]:
        if target_user:
            try:
                await chat.ban_member(target_user.id)
                await message.reply_text(f"🚫 تم طرد المستخدم: {target_user.first_name}")
            except Exception:
                await message.reply_text("عذراً، لا أملك صلاحية الطرد أو أن المستخدم مشرف.")
                
    elif text.startswith("كتم") and role in ["owner", "dev", "admin"]:
        if target_user:
            try:
                await context.bot.restrict_chat_member(chat.id, target_user.id, permissions={"can_send_messages": False})
                await message.reply_text(f"🔇 تم كتم المستخدم: {target_user.first_name}")
            except Exception:
                await message.reply_text("عذراً، لا أملك صلاحية الكتم.")

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_commands_handler))

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
