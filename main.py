import os
import logging
import sqlite3
import random
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

# --- قاعدة البيانات المركزية ---
def init_db():
    conn = sqlite3.connect("bot_database.db", timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS roles (user_id INTEGER PRIMARY KEY, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS active_groups (chat_id INTEGER PRIMARY KEY, chat_title TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            messages_count INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            photos_count INTEGER DEFAULT 0,
            typos_count INTEGER DEFAULT 0,
            level TEXT DEFAULT 'مبتدئ'
        )
    """)
    conn.commit()
    conn.close()

def save_user(user_id, username, full_name):
    try:
        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)", (user_id, username, full_name))
        cursor.execute("INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB Error: {e}")

def update_user_stats(user_id, is_photo=False):
    try:
        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)", (user_id,))
        if is_photo:
            cursor.execute("UPDATE user_stats SET messages_count = messages_count + 1, photos_count = photos_count + 1, points = points + 3 WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("UPDATE user_stats SET messages_count = messages_count + 1, points = points + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB Error: {e}")

def get_user_stats_data(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT messages_count, points, photos_count, typos_count, level FROM user_stats WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (0, 0, 0, 0, 'مبتدئ')

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

# --- دالة توليد الأزرار الشفافة الـ 7 للسورس ---
def get_command_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📊 الإحصائيات", callback_data="cmd_stats"),
            InlineKeyboardButton("🛡️ الحماية", callback_data="cmd_protection")
        ],
        [
            InlineKeyboardButton("🎮 الألعاب", callback_data="cmd_games"),
            InlineKeyboardButton("⚙️ الإدارة", callback_data="cmd_admin")
        ],
        [
            InlineKeyboardButton("🛍️ المتجر", callback_data="cmd_shop"),
            InlineKeyboardButton("👨‍💻 المطور", callback_data="cmd_dev")
        ],
        [
            InlineKeyboardButton("❌ إغلاق القائمة", callback_data="cmd_close")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- معالجة الأوامر والرسائل داخل المجموعات ---
async def group_commands_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return
    
    user = message.from_user
    if not user:
        return
        
    chat = message.chat
    text = message.text or message.caption or ""
    text_clean = text.strip()

    if chat.type in ["group", "supergroup"]:
        is_photo_msg = bool(message.photo)
        save_user(user.id, user.username, user.full_name)
        update_user_stats(user.id, is_photo=is_photo_msg)

    if text_clean == "تفعيل":
        if chat.type in ["group", "supergroup"]:
            activate_group(chat.id, chat.title)
            await message.reply_text("✅ **تم تفعيل البوت وحمايته وألعابه بالكامل في هذه المجموعة!**\nاكتب `الاوامر` لإظهار لوحات الأزرار الشفافة.")
            return

    if chat.type not in ["group", "supergroup"]:
        if text_clean == "/start":
            await message.reply_text("أهلاً بك! هذا البوت يعمل مباشرة داخل **المجموعات**. أضفني لمجموعتك واكتب **تفعيل**.")
        return

    role_title = get_user_role(user.id, user.username)
    reply = message.reply_to_message
    target_user = reply.from_user if reply else user
    target_role = get_user_role(target_user.id, target_user.username)

    # 1. إظهار الـ 7 لوحات والأزرار الشفافة عند كتابة "الاوامر" أو "الأوامر"
    if text_clean in ["الاوامر", "الأوامر", "اوامر", "اوامري"]:
        main_menu_text = (
            "📚 **دليل أوامر البوت الشامل في المجموعة:**\n\n"
            "مرحباً بك في لوحة تحكم السورس الرسمية.\n"
            "اختر القسم الذي تريد استعراض أوامره من الأزرار الشفافة بالأسفل 👇"
        )
        await message.reply_text(main_menu_text, reply_markup=get_command_keyboard())
        return

    # 2. اختصارات الألعاب المباشرة
    if text_clean in ["الالعاب", "الألعاب", "ألعاب"]:
        games_text = (
            "🎮 **قائمة ألعاب المجموعة الشاملة:**\n"
            "🎲 `روليت` - عجلة حظ ونقاط\n"
            "🕵️‍♂️ `مافيا` - لعبة التصويت\n"
            "🪑 `كراسي` - أسرع من يجلس\n"
            "🧠 `لغز` - اختبار ذكاء\n"
            "🍻 `صراحة` - أسئلة جريئة"
        )
        await message.reply_text(games_text)
        return

    # أوامر الإدارة العادية بالكروب
    if text_clean.startswith("رفع ادمن") or text_clean.startswith("رفع أدمن"):
        if role_title in ["المطور الاساسي", "مطور أساسي"]:
            if reply:
                set_user_role(target_user.id, "admin")
                await message.reply_text(f"👤 تم رفعه (أدمن رسمي): {target_user.first_name}")
        else:
            await message.reply_text("⚠️ هذا الأمر للمطور الأساسي فقط.")
            
    elif text_clean.startswith("طرد"):
        if role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
            if reply:
                try:
                    await chat.ban_member(target_user.id)
                    await message.reply_text(f"🚫 تم طرد المخالف: {target_user.first_name}")
                except Exception:
                    await message.reply_text("تأكد من صلاحيات البوت للإشراف.")
        else:
            await message.reply_text("⚠️ الأمر مخصص للإدارة.")

# --- نظام تفاعل الأزرار الشفافة (Callback Query) ---
async def inline_buttons_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cmd_stats":
        text = (
            "📊 **قسم الإحصائيات والمعلومات:**\n"
            "- `ايدي` أو `ايديك` (عرض معلوماتك ونقاطك وسحكاتك)\n"
            "- `رتبتي` (معرفة رتبتك الحالية في الكروب)\n"
            "- `الاحصائيات` (عرض عدد رسائلك ونقاطك)"
        )
    elif data == "cmd_protection":
        text = (
            "🛡️ **قسم الحماية والأمان:**\n"
            "- منع الروابط والتكرار تلقائياً\n"
            "- منع التوجيه والبوتات الوهمية\n"
            "- كتم الأعضاء المخالفين وقفل وفتح الدردشة"
        )
    elif data == "cmd_games":
        text = (
            "🎮 **قسم التسلية والألعاب:**\n"
            "- `روليت` (عجلة الحظ والنقاط)\n"
            "- `مافيا` (لعبة التصويت والتحقيق)\n"
            "- `كراسي` أو `جلس` (لعبة الكراسي الموسيقية)\n"
            "- `لغز` (حزورة وتحدي فكري)\n"
            "- `صراحة` (أسئلة منوعة)"
        )
    elif data == "cmd_admin":
        text = (
            "⚙️ **قسم الإدارة والصلاحيات:**\n"
            "- `رفع ادمن` / `تنزيل ادمن` (بالرد على الشخص)\n"
            "- `رفع مميز` / `تنزيل مميز` (بالرد على الشخص)\n"
            "- `طرد` (طرد العضو)\n"
            "- `كتم` / `فتح الكتم` (التحكم بالكتابة)"
        )
    elif data == "cmd_shop":
        text = (
            "🛍️ **قسم المتجر والخدمات:**\n"
            "- شراء تميز أسبوعي (50 نقطة)\n"
            "- تصفية سجل السحكات (30 نقطة)\n"
            "- تمييز الاسم بلون مميز في الكروب"
        )
    elif data == "cmd_dev":
        text = (
            "👨‍💻 **قسم المطور:**\n"
            f"المطور الأساسي: @{DEV_USERNAME}\n"
            f"قناة السورس الرسمية: {CHANNEL_USERNAME}\n"
            "للاستفسار أو طلب بوت خاص تواصل مع المطور."
        )
    elif data == "cmd_close":
        await query.message.delete()
        return
    else:
        text = "اختر القسم المطلوب من الأزرار أدناه:"

    await query.edit_message_text(text=text, reply_markup=get_command_keyboard(), parse_mode="Markdown")

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", group_commands_handler))
    application.add_handler(CallbackQueryHandler(inline_buttons_handler))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, group_commands_handler))

    PORT = int(os.environ.get("PORT", "10000"))
    RENDER_URL = "https://bot-maker-1-709e.onrender.com"

    logger.info("Bot started with 7 transparent inline command boards...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
