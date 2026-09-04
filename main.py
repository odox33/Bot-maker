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
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('forced_sub', 'active')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('paid_bots_active', 'active')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('free_bots_active', 'active')")
    cursor.execute("CREATE TABLE IF NOT EXISTS roles (user_id INTEGER PRIMARY KEY, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS active_groups (chat_id INTEGER PRIMARY KEY, chat_title TEXT)")
    # جدول إحصائيات المستخدمين (رسائل، نقاط، صور، سحكات)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            messages_count INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            photos_count INTEGER DEFAULT 0,
            typos_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_user(user_id, username, full_name):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)", (user_id, username, full_name))
    cursor.execute("INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def update_user_stats(user_id, is_photo=False):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)", (user_id,))
    if is_photo:
        cursor.execute("UPDATE user_stats SET messages_count = messages_count + 1, photos_count = photos_count + 1, points = points + 2 WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("UPDATE user_stats SET messages_count = messages_count + 1, points = points + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_user_stats_data(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT messages_count, points, photos_count, typos_count FROM user_stats WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (0, 0, 0, 0)

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
        return "المطور الاساسي"
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM roles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        roles_map = {"dev": "مطور أساسي", "admin": "أدمن", "vip": "عضو مميز"}
        return roles_map.get(row[0], "عضو")
    return "عضو"

def set_user_role(user_id, role):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO roles (user_id, role) VALUES (?, ?)", (user_id, role))
    conn.commit()
    conn.close()

def activate_group(chat_id, chat_title):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO active_groups (chat_id, chat_title) VALUES (?, ?)", (chat_id, chat_title))
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
    chat = update.effective_chat
    save_user(user.id, user.username, user.full_name)
    role_title = get_user_role(user.id, user.username)
    
    if chat.type in ["group", "supergroup"]:
        await update.message.reply_text("أهلاً بك! البوت يعمل في هذه المجموعة. اكتب **تفعيل** لتفعيل البوت رسمياً.")
        return

    if role_title == "المطور الاساسي":
        keyboard = [
            [InlineKeyboardButton("⚙️ إعدادات البوت والتحكم الأساسي", callback_data="admin_settings")],
            [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
            [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
            [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
            [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
        ]
        welcome_text = f"أهلاً بك يا مطورنا الأساسي في لوحة تحكم المنصة الرئيسية:"
    else:
        keyboard = [
            [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
            [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
            [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
            [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
        ]
        welcome_text = f"أهلاً بك يا {user.first_name} في منصة صناعة وإدارة البوتات."

    reply_markup = InlineKeyboardMarkup(keyboard)
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
    role_title = get_user_role(user.id, user.username)
    await query.answer()
    
    if query.data == "free_bot_maker":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(text="🛠 **قسم صانع البوتات المجاني:**\n\nأرسل توكن بوتك الجديد للبدء بصنعه.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif query.data == "paid_bot_maker":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(text="💎 **قسم صانع البوتات المدفوع:**\n\nبوتات احترافية بدون رعاية وبدون اشتراك إجباري!", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif query.data == "dev_contact":
        keyboard = [
            [InlineKeyboardButton("💬 مراسلة المطور", url=f"https://t.me/{DEV_USERNAME}")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
        ]
        await query.edit_message_text(text=f"👨‍💻 **معلومات المطور:**\nالمطور: @{DEV_USERNAME}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif query.data == "get_my_id":
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        stats = get_user_stats_data(user.id)
        username_str = f"@{user.username}" if user.username else "لا يوجد"
        text_id = (
            f"- : ايديك : ( {user.id} )\n"
            f"- : معرفك : ( {username_str} )\n"
            f"- : رتبتك : ( {role_title} )\n"
            f"- : رسائلك : ( {stats[0]} )\n"
            f"- : نقاطك : ( {stats[1]} )\n"
            f"- : سحكاتك : ( {stats[3]} )\n"
            f"- : صورك : ( {stats[2]} )"
        )
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        if photos.total_count > 0:
            photo_file_id = photos.photos[0][-1].file_id
            await query.message.delete()
            await context.bot.send_photo(chat_id=user.id, photo=photo_file_id, caption=text_id, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(text=text_id, reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "back_to_start":
        if role_title == "المطور الاساسي":
            keyboard = [
                [InlineKeyboardButton("⚙️ إعدادات البوت والتحكم الأساسي", callback_data="admin_settings")],
                [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
                [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
                [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
                [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
                [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
                [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
                [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
            ]
        await query.edit_message_text(text="القائمة الرئيسية:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- الأوامر ورسائل المجموعات ---
async def group_commands_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return
    
    user = message.from_user
    if not user:
        return
        
    chat = message.chat
    text = message.text or message.caption or ""
    text = text.strip()

    # تتبع الرسائل والإحصائيات في الكروبات
    if chat.type in ["group", "supergroup"]:
        is_photo_msg = bool(message.photo)
        save_user(user.id, user.username, user.full_name)
        update_user_stats(user.id, is_photo=is_photo_msg)

    # أمر التفعيل
    if text == "تفعيل":
        if chat.type in ["group", "supergroup"]:
            activate_group(chat.id, chat.title)
            await message.reply_text("تم تفعيل البوت بنجاح! ✅")
            return

    if chat.type not in ["group", "supergroup"]:
        return

    role_title = get_user_role(user.id, user.username)
    reply = message.reply_to_message
    target_user = reply.from_user if reply else user
    target_role = get_user_role(target_user.id, target_user.username)

    # أمر الايدي داخل المجموعة
    if text == "ايدي" or text == "/id":
        photos = await context.bot.get_user_profile_photos(target_user.id, limit=1)
        stats = get_user_stats_data(target_user.id)
        username_str = f"@{target_user.username}" if target_user.username else "لا يوجد"
        
        text_id = (
            f"- : ايديك : ( {target_user.id} )\n"
            f"- : معرفك : ( {username_str} )\n"
            f"- : رتبتك : ( {target_role} )\n"
            f"- : رسائلك : ( {stats[0]} )\n"
            f"- : نقاطك : ( {stats[1]} )\n"
            f"- : سحكاتك : ( {stats[3]} )\n"
            f"- : صورك : ( {stats[2]} )"
        )
        
        if photos.total_count > 0:
            photo_file_id = photos.photos[0][-1].file_id
            await message.reply_photo(photo=photo_file_id, caption=text_id)
        else:
            await message.reply_text(text_id)
        return

    # أوامر الرفع والتنزيل
    if text.startswith("رفع مطور أساسي") and role_title == "المطور الاساسي":
        if reply:
            set_user_role(target_user.id, "dev")
            await message.reply_text(f"👤 تم رفعه (مطور أساسي): {target_user.first_name}")
    elif text.startswith("رفع أدمن") and role_title in ["المطور الاساسي", "مطور أساسي"]:
        if reply:
            set_user_role(target_user.id, "admin")
            await message.reply_text(f"👤 تم رفعه (أدمن): {target_user.first_name}")
    elif text.startswith("رفع مميز") and role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
        if reply:
            set_user_role(target_user.id, "vip")
            await message.reply_text(f"⭐ تم رفعه (عضو مميز): {target_user.first_name}")
            
    # أوامر الطرد والكتم
    elif text.startswith("طرد") and role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
        if reply:
            try:
                await chat.ban_member(target_user.id)
                await message.reply_text(f"🚫 تم طرد المستخدم: {target_user.first_name}")
            except Exception:
                await message.reply_text("عذراً، تأكد من صلاحيات البوت الإدارية في المجموعة.")
                
    elif text.startswith("كتم") and role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
        if reply:
            try:
                await context.bot.restrict_chat_member(chat.id, target_user.id, permissions={"can_send_messages": False})
                await message.reply_text(f"🔇 تم كتم المستخدم: {target_user.first_name}")
            except Exception:
                await message.reply_text("عذراً، تأكد من صلاحيات البوت الإدارية في المجموعة.")

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("id", lambda u, c: group_commands_handler(u, c)))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, group_commands_handler))

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
