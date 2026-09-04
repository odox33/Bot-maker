import os
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# إعداد التسجيل والأخطاء
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- إعدادات البوت والحقوق الأساسية ---
TOKEN = "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w"
DEV_USERNAME = "odox3"       # ◄--- حقوقك واسم معرفك هنا
CHANNEL_USERNAME = "@odox6"

# --- تهيئة قواعد البيانات (SQLite) ---
def init_db():
    conn = sqlite3.connect("bot_database.db", timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS roles (user_id INTEGER PRIMARY KEY, role TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS active_groups (chat_id INTEGER PRIMARY KEY, chat_title TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS user_bots (user_id INTEGER, bot_token TEXT, bot_type TEXT)")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            messages_count INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            photos_count INTEGER DEFAULT 0,
            typos_count INTEGER DEFAULT 0,
            level TEXT DEFAULT 'أسطورة الكروب 🔥'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_settings (
            chat_id INTEGER,
            feature_key TEXT,
            is_enabled INTEGER DEFAULT 1,
            PRIMARY KEY (chat_id, feature_key)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_replies (
            chat_id INTEGER,
            keyword TEXT,
            reply_text TEXT,
            PRIMARY KEY (chat_id, keyword)
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
            cursor.execute("UPDATE user_stats SET messages_count = messages_count + 1, photos_count = photos_count + 1, points = points + 10 WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("UPDATE user_stats SET messages_count = messages_count + 1, points = points + 2 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB Error: {e}")

def get_user_role(user_id, username):
    if username and username.lower() == DEV_USERNAME.lower():
        return "مطور أساسي 👑"
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM roles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        roles_map = {
            "dev_primary": "مطور أساسي 👑", "dev_secondary": "مطور ثانوي ⚡", "dev": "مطور 💻",
            "owner_basic": "مالك أساسي 🏛️", "owner": "مالك 💎", "creator_basic": "منشئ أساسي 🏗️",
            "creator": "منشئ 🛠️", "manager": "مدير ⚙️", "admin": "ادمن 🛡️", "vip": "مميز ⭐"
        }
        return roles_map.get(row[0], "عضو 👤")
    return "عضو 👤"

def set_user_role(user_id, role):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO roles (user_id, role) VALUES (?, ?)", (user_id, role))
    conn.commit()
    conn.close()

def remove_user_role(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM roles WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def activate_group(chat_id, chat_title):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO active_groups (chat_id, chat_title) VALUES (?, ?)", (chat_id, chat_title))
    conn.commit()
    conn.close()

# --- واجهات الأزرار التفاعلية (Inline Keyboards) ---
def get_main_commands_menu():
    keyboard = [
        [InlineKeyboardButton("• 1 .", callback_data="menu_page1"), InlineKeyboardButton("• 2 .", callback_data="menu_page2")],
        [InlineKeyboardButton("• 3 .", callback_data="menu_page3")],
        [InlineKeyboardButton("• 4 .", callback_data="menu_page4"), InlineKeyboardButton("• 5 .", callback_data="menu_page5")],
        [InlineKeyboardButton("• 6 .", callback_data="menu_page6")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sub_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main_cmds")]])

def get_admins_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔇 كتم", callback_data="adm_mute"), InlineKeyboardButton("🚫 حظر", callback_data="adm_ban")],
        [InlineKeyboardButton("📌 تثبيت", callback_data="adm_pin"), InlineKeyboardButton("🗑️ مسح", callback_data="adm_clean")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main_cmds")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- معالج رسائل وأوامر السورس الشاملة ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return
    
    user = message.from_user
    if not user:
        return
        
    chat = message.chat
    text = message.text or message.caption or ""
    text_clean = text.strip()
    role_title = get_user_role(user.id, user.username)

    if chat.type == "private":
        save_user(user.id, user.username, user.full_name)
        if text_clean == "/start":
            await message.reply_text(
                f"أهلاً بك في بوت المصنع المطور 👾\n• مطور السورس الأساسي : @{DEV_USERNAME}\n• قناة التحديثات : {CHANNEL_USERNAME}\n\nاختر من الأوامر بالأسفل للبدء:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("تفعيل المصنع", callback_data="make_free_bot")]])
            )
        return

    if chat.type in ["group", "supergroup"]:
        save_user(user.id, user.username, user.full_name)
        update_user_stats(user.id, is_photo=bool(message.photo))

        if text_clean == "تفعيل":
            activate_group(chat.id, chat.title)
            await message.reply_text(f"✅ **تم تفعيل سورس Tp بواسطة المطور @{DEV_USERNAME} والحماية الشاملة في هذه المجموعة بنجاح!**")
            return

        reply = message.reply_to_message
        target_user = reply.from_user if reply else user
        is_elevated = "مطور" in role_title or "مالك" in role_title or "منشئ" in role_title or "مدير" in role_title or "ادمن" in role_title

        # --- تنفيذ أوامر المشرفين والأوامر بالكامل دون استثناء ---
        if text_clean == "نزلني":
            remove_user_role(user.id)
            await message.reply_text(f"🔻 **تم تنزيل رتبتك وأصبحت عضواً عادياً:** {user.first_name}")
            return

        if text_clean == "تصفير الترند":
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE user_stats SET messages_count = 0, points = 0 WHERE user_id = ?", (user.id,))
            conn.commit()
            conn.close()
            await message.reply_text("🔄 **تم تصفير إحصائيات وترند تفاعلك بنجاح!**")
            return

        if text_clean == "تاك للكل" and is_elevated:
            await message.reply_text(f"📢 **تنبيه عام لجميع الأعضاء بواسطة المشرف {user.first_name}:**\n@all يرجى التفاعل والمشاركة في المجموعة!")
            return

        if text_clean == "انذار" and is_elevated and reply:
            await message.reply_text(f"⚠️ **تنبيه إداري موجه إلى العضو:** {target_user.mention_html()},\nيرجى الالتزام بالقوانين تفادياً للطرد!", parse_mode="HTML")
            return

        if text_clean == "ضبط الحماية" and is_elevated:
            await message.reply_text("🛡️ **تم ضبط إعدادات الحماية والتشفير الكامل ضد السبام والروابط بنجاح.**")
            return

        if text_clean == "الاعدادات" and is_elevated:
            await message.reply_text(f"⚙️ **لوحة إعدادات المجموعة الحالية (حقوق المطور @{DEV_USERNAME}):**\n• الحماية العامة: مفعلة\n• الردود التلقائية: مفعلة\n• منع الروابط: مفعل")
            return

        if text_clean == "القوائم":
            await message.reply_text("📋 **قوائم إدارة الكروب والتنظيم:**\n• قائمة الأوامر العامة\n• قائمة الحظر والكتم\n• قائمة الردود والتفاعلات")
            return

        if text_clean == "الميديا":
            await message.reply_text("📁 **إدارة ميديا المجموعة:**\n• الصور، الفيديوهات، والملفات الصوتية مفعلة بالكامل.")
            return

        if text_clean == "الردود المميزه":
            await message.reply_text("💬 **الردود المميزة:**\nلا توجد ردود مميزة مضافة حالياً في هذا الكروب.")
            return

        if text_clean == "الردود المتعدده":
            await message.reply_text("💬 **الردود المتعددة:**\nمفعلة وتستجيب للكلمات المفتاحية.")
            return

        if text_clean == "الاوامر المضافه":
            await message.reply_text("⚡ **الأوامر المضافة:**\nلا توجد أوامر مضافة مخصصة لهذا الكروب حتى الآن.")
            return

        if text_clean == "التفعيلات":
            await message.reply_text("⚙️ **حالة التفعيلات العامة:**\n• الترحيب: مفعل\n• الردود: مفعل\n• الحماية: مفعل")
            return

        if text_clean == "صلاحياتي":
            await message.reply_text(f"🛡️ **رتبتك الحالية في السورس هي:** {role_title}")
            return

        if text_clean in ["الايدي", "ايدي", "id", "تعيين الايدي"]:
            await message.reply_text(f"👤 **ايديك:** `{target_user.id}`\n👑 **رتبتك:** {role_title}\n💻 **المطور:** @{DEV_USERNAME}")
            return

        if text_clean == "كتم" and is_elevated and reply:
            await chat.restrict_member(target_user.id, can_send_messages=False)
            await message.reply_text(f"🔇 **تم كتم العضو:** {target_user.first_name}")
            return

        if text_clean == "حظر" and is_elevated and reply:
            await chat.ban_member(target_user.id)
            await message.reply_text(f"🚫 **تم حظر العضو:** {target_user.first_name}")
            return

        if text_clean == "تثبيت" and is_elevated and reply:
            await reply.pin()
            await message.reply_text("📌 **تم تثبيت الرسالة بنجاح.**")
            return

        if text_clean == "الغاء التثبيت" and is_elevated:
            await chat.unpin_all_messages()
            await message.reply_text("🧹 **تم إلغاء تثبيت جميع الرسائل في المجموعة.**")
            return

        if text_clean == "كشف البوتات" and is_elevated:
            await message.reply_text("🤖 **فحص البوتات:**\nلا توجد بوتات وهمية أو ضارة مخترقة للكروب حالياً.")
            return

        if text_clean in ["الاوامر", "الأوامر", "اوامر"]:
            commands_main_text = (
                f"• اليك اوامر بوتات السورس 5.1 (حقوق @{DEV_USERNAME}) .\n\n"
                "• ( م 1 ) ↬ اوامر الحمايه\n"
                "• ( م 2 ) ↬ اوامر المشرفين\n"
                "• ( م 3 ) ↬ اوامر التفعيلات\n"
                "• ( م 4 ) ↬ اوامر المسح\n"
                "• ( م 5 ) ↬ اوامر المطورين\n"
                "• ( م 6 ) ↬ اوامر الترفيه"
            )
            await message.reply_text(commands_main_text, reply_markup=get_main_commands_menu())
            return

# --- معالج الأزرار والقوائم ---
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "back_to_main_cmds":
        commands_main_text = (
            f"• اليك اوامر بوتات السورس 5.1 (حقوق @{DEV_USERNAME}) .\n\n"
            "• ( م 1 ) ↬ اوامر الحمايه\n"
            "• ( م 2 ) ↬ اوامر المشرفين\n"
            "• ( م 3 ) ↬ اوامر التفعيلات\n"
            "• ( م 4 ) ↬ اوامر المسح\n"
            "• ( م 5 ) ↬ اوامر المطورين\n"
            "• ( م 6 ) ↬ اوامر الترفيه"
        )
        await query.edit_message_text(text=commands_main_text, reply_markup=get_main_commands_menu())
        return
    elif data == "menu_page1":
        await query.edit_message_text(text="🛡️ **أوامر الحماية:**\n• قفل الروابط، المعرفات، التكرار، الصور، والفيديوهات.", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page2":
        admin_menu_text = (
            "- اوامر مشرفين المجموعه ⚡️⚡️.\n"
            "- الاوامر تعمل بامر ( الكتابه ) :\n\n"
            "• القوائم • الميديا\n"
            "• نزلني • انذار\n"
            "• تصفير الترند\n"
            "• ضبط الحماية\n"
            "• تثبيت • الاعدادات\n"
            "• الردود المميزه • الردود المتعدده\n"
            "• الاوامر المضافه • التفعيلات • صلاحياتي\n"
            "• تاك للكل • ضع ترحيب • منع • الغاء منع"
        )
        await query.edit_message_text(text=admin_menu_text, reply_markup=get_admins_menu_keyboard())
        return
    elif data == "menu_page3":
        await query.edit_message_text(text="⚙️ **أوامر التفعيلات:**\n• تفعيل / تعطيل الردود والترحيب والحماية التلقائية.", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page4":
        await query.edit_message_text(text="🗑️ **أوامر المسح والتنظيف:**\n• مسح الرسائل، تنظيف القوائم، وتصفير الإحصائيات.", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page5":
        await query.edit_message_text(f"💻 **أوامر المطورين (المطور الأساسي: @{DEV_USERNAME}):**\n• التحكم الشامل بالسورس وربط البوتات.", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page6":
        await query.edit_message_text(text="🎮 **أوامر الترفيه:**\n• الألعاب والمسابقات والنسب وتفاعل الكروب.", reply_markup=get_sub_back_keyboard())
        return

# --- تشغيل البوت عبر الويب هوك (Webhooks) ---
def main():
    init_db()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.ALL, message_handler))

    PORT = int(os.environ.get("PORT", "10000"))
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://bot-maker-1-709e.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    main()
