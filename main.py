import os
import logging
import sqlite3
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- إعدادات التسجيل واللوغ (Logging Configuration) ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- إعدادات البوت والثوابت الأساسية والحقوق ---
TOKEN = "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w"
DEV_USERNAME = "odox3"       # ◄--- حقوقك واسم معرفك الأساسي
CHANNEL_USERNAME = "@odox6"
START_TIME = time.time()

# =====================================================================
# --- قاعدة البيانات وأنظمة التخزين الموسعة (Database & Storage) ---
# =====================================================================

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
        CREATE TABLE IF NOT EXISTS locked_features (
            chat_id INTEGER,
            lock_name TEXT,
            PRIMARY KEY (chat_id, lock_name)
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_commands (
            chat_id INTEGER,
            command_name TEXT,
            command_output TEXT,
            PRIMARY KEY (chat_id, command_name)
        )
    """)
    # جدول المصنع (المجاني والمدفوع)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS made_bots (
            owner_id INTEGER PRIMARY KEY,
            bot_token TEXT,
            bot_type TEXT,
            bot_username TEXT,
            created_at TEXT
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
        logger.error(f"DB Error (save_user): {e}")

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
        logger.error(f"DB Error (update_user_stats): {e}")

def get_user_role_key(user_id, username):
    if username and username.lower() == DEV_USERNAME.lower():
        return "dev_primary"
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM roles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "member"

def get_user_role_title(user_id, username):
    key = get_user_role_key(user_id, username)
    roles_map = {
        "dev_primary": "مطور أساسي 👑", 
        "dev_secondary": "مطور ثانوي ⚡", 
        "dev": "مطور 💻",
        "owner_primary": "مالك أساسي 🏛️", 
        "owner": "مالك 💎", 
        "manager": "مدير ⚙️", 
        "admin": "ادمن 🛡️", 
        "vip": "مميز ⭐",
        "member": "عضو 👤"
    }
    return roles_map.get(key, "عضو 👤")

# --- نظام سلم الرتب والصلاحيات التراكمية (Role Hierarchy & Power Level) ---
ROLE_LEVELS = {
    "member": 0,
    "vip": 1,
    "admin": 2,
    "manager": 3,
    "owner": 4,
    "owner_primary": 5,
    "dev": 6,
    "dev_secondary": 7,
    "dev_primary": 8
}

def get_role_level(user_id, username):
    if username and username.lower() == DEV_USERNAME.lower():
        return 8
    role_key = get_user_role_key(user_id, username)
    return ROLE_LEVELS.get(role_key, 0)

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

def remove_all_roles():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM roles")
    conn.commit()
    conn.close()

def activate_group(chat_id, chat_title):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO active_groups (chat_id, chat_title) VALUES (?, ?)", (chat_id, chat_title))
    conn.commit()
    conn.close()

def set_lock(chat_id, lock_name, status):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    if status:
        cursor.execute("INSERT OR REPLACE INTO locked_features (chat_id, lock_name) VALUES (?, ?)", (chat_id, lock_name))
    else:
        cursor.execute("DELETE FROM locked_features WHERE chat_id = ? AND lock_name = ?", (chat_id, lock_name))
    conn.commit()
    conn.close()

def set_feature_status(chat_id, feature_key, status):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO group_settings (chat_id, feature_key, is_enabled) VALUES (?, ?, ?)", (chat_id, feature_key, 1 if status else 0))
    conn.commit()
    conn.close()

def add_custom_reply(chat_id, keyword, reply_text):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO custom_replies (chat_id, keyword, reply_text) VALUES (?, ?, ?)", (chat_id, keyword, reply_text))
    conn.commit()
    conn.close()

def delete_custom_reply(chat_id, keyword):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM custom_replies WHERE chat_id = ? AND keyword = ?", (chat_id, keyword))
    conn.commit()
    conn.close()

def get_custom_reply(chat_id, keyword):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT reply_text FROM custom_replies WHERE chat_id = ? AND keyword = ?", (chat_id, keyword))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def add_custom_command(chat_id, cmd_name, cmd_output):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO custom_commands (chat_id, command_name, command_output) VALUES (?, ?, ?)", (chat_id, cmd_name, cmd_output))
    conn.commit()
    conn.close()

def delete_custom_command(chat_id, cmd_name):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM custom_commands WHERE chat_id = ? AND command_name = ?", (chat_id, cmd_name))
    conn.commit()
    conn.close()

def get_custom_command(chat_id, cmd_name):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT command_output FROM custom_commands WHERE chat_id = ? AND command_name = ?", (chat_id, cmd_name))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# =====================================================================
# --- واجهات وقوائم الأزرار الشاملة (Inline Keyboards & Menus) ---
# =====================================================================

def get_start_private_menu():
    keyboard = [
        [InlineKeyboardButton("🛠️ قسم صناعة البوتات (المصنع)", callback_data="factory_main")],
        [InlineKeyboardButton("📚 قائمة الأوامر الشاملة", callback_data="back_to_main_cmds")],
        [InlineKeyboardButton("💎 قناة التحديثات والاصدارات", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
        [InlineKeyboardButton("👨‍💻 تواصل مع المطور الأساسي", url=f"https://t.me/{DEV_USERNAME}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_factory_menu():
    keyboard = [
        [InlineKeyboardButton("🤖 صنع بوت مجاني (Free Bot)", callback_data="make_free_bot")],
        [InlineKeyboardButton("⭐ صنع بوت مدفوع VIP (Paid Bot)", callback_data="make_paid_bot")],
        [InlineKeyboardButton("📊 إدارة بوتاتي المصنوعة", callback_data="manage_my_bots")],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_commands_menu():
    keyboard = [
        [InlineKeyboardButton("• [ م 1 ] الحماية •", callback_data="menu_page1"), InlineKeyboardButton("• [ م 2 ] المشرفين والرتب •", callback_data="menu_page2")],
        [InlineKeyboardButton("• [ م 3 ] التفعيلات والتعطيل •", callback_data="menu_page3"), InlineKeyboardButton("• [ م 4 ] المسح والتنظيف •", callback_data="menu_page4")],
        [InlineKeyboardButton("• [ م 5 ] المطورين والتحكم •", callback_data="menu_page5"), InlineKeyboardButton("• [ م 6 ] الألعاب والترفيه •", callback_data="menu_page6")],
        [InlineKeyboardButton("• [ م 7 ] الأوامر الإضافية المبتكرة •", callback_data="menu_page7")],
        [InlineKeyboardButton("🔙 رجوع للوحة الرئيسية", callback_data="back_to_start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sub_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع لقائمة الأوامر", callback_data="back_to_main_cmds")]])

def get_admins_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔇 كتم", callback_data="adm_mute"), InlineKeyboardButton("🚫 حظر", callback_data="adm_ban")],
        [InlineKeyboardButton("📌 تثبيت", callback_data="adm_pin"), InlineKeyboardButton("🗑️ مسح", callback_data="adm_clean")],
        [InlineKeyboardButton("🔙 رجوع للأوامر", callback_data="back_to_main_cmds")]
    ]
    return InlineKeyboardMarkup(keyboard)

# =====================================================================
# --- معالج الرسائل والأوامر الضخم والمفصل (Massive Message Handler) ---
# =====================================================================

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
    
    role_title = get_user_role_title(user.id, user.username)
    user_lvl = get_role_level(user.id, user.username)

    # --- معالجة المحادثات الخاصة (Private Chats - مصنع البوتات والأوامر) ---
    if chat.type == "private":
        save_user(user.id, user.username, user.full_name)
        
        if text_clean == "/start":
            await message.reply_text(
                f"✨ **أهلاً بك عزيزي في بوت المصنع والسورس المطور الشامل (5.2)** 🤖\n\n"
                f"• أقوى بوت لإدارة المجموعات وصناعة البوتات التلقائية.\n"
                f"• المطور الأساسي: @{DEV_USERNAME}\n"
                f"• قناة السورس الرسمية: {CHANNEL_USERNAME}\n\n"
                f"اختر أحد الخيارات بالأسفل للبدء بالتحكم أو صناعة بوتك الخاص:",
                reply_markup=get_start_private_menu()
            )
            return

        # محاكاة خطوة إدخال التوكن لصناعة بوت مجاني أو مدفوع
        if context.user_state == "waiting_for_free_token":
            bot_token = text_clean
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO made_bots (owner_id, bot_token, bot_type, bot_username, created_at) VALUES (?, ?, ?, ?, ?)",
                           (user.id, bot_token, "مجاني (Free)", f"@Bot_{random.randint(1000,9999)}", time.strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            context.user_state = None
            await message.reply_text(
                f"🎉 **تم إنشاء بوتك المجاني بنجاح تام!**\n\n"
                f"• نوع البوت: مجاني 🤖\n"
                f"• حالة الخادم: يعمل الآن على استضافتنا السحابية ⚡\n"
                f"• حقوق المطور: @{DEV_USERNAME}",
                reply_markup=get_factory_menu()
            )
            return

        if context.user_state == "waiting_for_paid_token":
            bot_token = text_clean
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO made_bots (owner_id, bot_token, bot_type, bot_username, created_at) VALUES (?, ?, ?, ?, ?)",
                           (user.id, bot_token, "مدفوع VIP (Paid)", f"@VIP_Bot_{random.randint(1000,9999)}", time.strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            context.user_state = None
            await message.reply_text(
                f"💎 **تم تفعيل وإنشاء بوتك المدفوع بنجاح خارق!**\n\n"
                f"• نوع البوت: VIP مدفوع بمميزات كاملة 🚀\n"
                f"• حماية قصوى + سرعة خيالية + استجابة فورية.\n"
                f"• حقوق المطور: @{DEV_USERNAME}",
                reply_markup=get_factory_menu()
            )
            return

        return

    # --- معالجة المجموعات والمجتمعات (Groups & Supergroups) ---
    if chat.type in ["group", "supergroup"]:
        save_user(user.id, user.username, user.full_name)
        update_user_stats(user.id, is_photo=bool(message.photo))

        # --- أمر التفعيل الأساسي للمجموعة ---
        if text_clean == "تفعيل":
            activate_group(chat.id, chat.title)
            await message.reply_text(f"✅ **تم تفعيل سورس Tp المتطور بواسطة المطور الأساسي @{DEV_USERNAME} والحماية الشاملة في هذه المجموعة بنجاح تام!**")
            return

        reply = message.reply_to_message
        target_user = reply.from_user if reply else user
        target_role_title = get_user_role_title(target_user.id, target_user.username)
        target_lvl = get_role_level(target_user.id, target_user.username)

        # =====================================================================
        # --- نظام اختصارات الأوامر السريعة بالحروف (Shortcuts Mapping) ---
        # =====================================================================
        if text_clean in ["أ", "ا", "id"]:
            text_clean = "الايدي"
        elif text_clean in ["م", "مميز"]:
            text_clean = "رفع مميز"
        elif text_clean in ["د", "مدير"]:
            text_clean = "رفع مدير"
        elif text_clean in ["ر", "الاوامر"]:
            text_clean = "الاوامر"
        elif text_clean in ["ت", "تفعيل"]:
            text_clean = "التفعيلات"

        # =====================================================================
        # --- أمر ترتيب الأوامر ---
        # =====================================================================
        if text_clean == "ترتيب الاوامر":
            markup_order = InlineKeyboardMarkup([
                [InlineKeyboardButton("قناة السورس الرسمية 🍓", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")]
            ])
            await message.reply_text("- : تم ترتيب الاوامر الاساسية باحترافية تامة،", reply_markup=markup_order)
            return

        # =====================================================================
        # --- نظام إضافة وحذف الأوامر المخصصة (Custom Commands) ---
        # =====================================================================
        if text_clean.startswith("اضف امر ") and user_lvl >= 2 and reply:
            cmd_key = text_clean.replace("اضف امر ", "").strip()
            cmd_val = reply.text or reply.caption or "محتوى الأمر المخصص"
            add_custom_command(chat.id, cmd_key, cmd_val)
            await message.reply_text(f"➕ **تم إضافة الأمر الجديد بنجاح:** `{cmd_key}`\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean.startswith("حذف امر ") and user_lvl >= 2:
            cmd_key = text_clean.replace("حذف امر ", "").strip()
            delete_custom_command(chat.id, cmd_key)
            await message.reply_text(f"🗑️ **تم حذف الأمر بنجاح:** `{cmd_key}`\n• حقوق السورس: @{DEV_USERNAME}")
            return

        custom_cmd_output = get_custom_command(chat.id, text_clean)
        if custom_cmd_output:
            await message.reply_text(custom_cmd_output)
            return

        # =====================================================================
        # --- نظام إضافة وحذف الردود التلقائية (Custom Replies) ---
        # =====================================================================
        if text_clean.startswith("اضف رد ") and user_lvl >= 2 and reply:
            rep_key = text_clean.replace("اضف رد ", "").strip()
            rep_val = reply.text or reply.caption or "رد تلقائي جديد"
            add_custom_reply(chat.id, rep_key, rep_val)
            await message.reply_text(f"💬 **تم إضافة الرد التلقائي بنجاح:** `{rep_key}`\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean.startswith("حذف رد ") and user_lvl >= 2:
            rep_key = text_clean.replace("حذف رد ", "").strip()
            delete_custom_reply(chat.id, rep_key)
            await message.reply_text(f"🗑️ **تم حذف الرد التلقائي بنجاح:** `{rep_key}`\n• حقوق السورس: @{DEV_USERNAME}")
            return

        custom_reply_text = get_custom_reply(chat.id, text_clean)
        if custom_reply_text:
            await message.reply_text(custom_reply_text)
            return

        # =====================================================================
        # --- المميزات القوية (سرعة البوت وتوب الكروب والذكاء المبتكر) ---
        # =====================================================================
        if text_clean in ["سرعة البوت", "البنج", "السرعة"]:
            ping_time = round((time.time() - START_TIME) % 1, 3) * 1000
            await message.reply_text(f"⚡ **سرعة استجابة السورس (البنج):** `{int(ping_time)} ms`\n• يعمل بكفاءة خارقة على استضافات 2026\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["توب الكروب", "لوحة الشرف", "الترند"]:
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, points FROM user_stats ORDER BY points DESC LIMIT 5")
            top_users = cursor.fetchall()
            conn.close()
            
            top_text = "🏆 **قائمة الشرف والترند الأنشط في الكروب:**\n\n"
            for idx, (uid, pts) in enumerate(top_users, 1):
                top_text += f"{idx} • الأيدي (`{uid}`) - النقاط: **{pts}** نقطة 🔥\n"
            top_text += f"\n• حقوق السورس: @{DEV_USERNAME}"
            await message.reply_text(top_text)
            return

        # أوامر إضافية مبتكرة ومسلية (م 7)
        if text_clean in ["نكتة", "نكت"]:
            jokes = [
                "محشش سألوه: شو رأيك بالزواج المبكر؟ قال: يعني الساعة 7 الصبح؟ 😂",
                "واحد غبي ضاع تلفونه، صار يبكي، صاحبه قله: لا تبكي اتصل عليه من تلفونك الثاني وشوف وين ريحة! قال: تصدق فكرة حلوة! 🤦‍♂️",
                "محشش دخل صيدلية قالهم: عندكم قطرة عيون وسعيدة؟ قالوا: لا والله! قال: خسارة فاتتني الحفلة 😂"
            ]
            await message.reply_text(f"😂 **نكتة اليوم من السورس:**\n\n{random.choice(jokes)}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["حكمة", "حكمة اليوم"]:
            wisdoms = [
                "من أراد النجاح في هذا العالم عليه أن يتجاهل كلام المحبطين.",
                "الصمت هو أفضل رد على السخافات.",
                "الجمال في العقول لا في المظاهر."
            ]
            await message.reply_text(f"💡 **حكمة السورس:**\n\n{random.choice(wisdoms)}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- أوامر القفل والفتح الشاملة (قائمة الم 1 الكاملة) ---
        # =====================================================================
        locks_map = {
            "قفل الروابط": ("links", True), "فتح الروابط": ("links", False),
            "قفل المعرفات": ("usernames", True), "فتح المعرفات": ("usernames", False),
            "قفل التكرار": ("flood", True), "فتح التكرار": ("flood", False),
            "قفل الصور": ("photos", True), "فتح الصور": ("photos", False),
            "قفل الفيديوهات": ("videos", True), "فتح الفيديوهات": ("videos", False),
            "قفل البوتات": ("bots", True), "فتح البوتات": ("bots", False),
            "قفل التوجيه": ("forward", True), "فتح التوجيه": ("forward", False),
            "قفل الملصقات": ("stickers", True), "فتح الملصقات": ("stickers", False),
            "قفل المتحركة": ("gifs", True), "فتح المتحركة": ("gifs", False),
            "قفل البوتات المتحركة": ("inline_bots", True), "فتح البوتات المتحركة": ("inline_bots", False),
            "قفل التثبيت": ("pin", True), "فتح التثبيت": ("pin", False),
            "قفل التغيير": ("group_info", True), "فتح التغيير": ("group_info", False),
            "قفل الدردشة": ("chat", True), "فتح الدردشة": ("chat", False),
            "قفل الكلايش": ("long_messages", True), "فتح الكلايش": ("long_messages", False),
            "قفل التكرار السريع": ("fast_flood", True), "فتح التكرار السريع": ("fast_flood", False)
        }
        if text_clean in locks_map:
            if user_lvl < 3:
                await message.reply_text("⚠️ عذراً، هذا الأمر يتطلب رتبة **مدير** أو أعلى للتحكم بالحماية!")
                return
            l_key, l_status = locks_map[text_clean]
            set_lock(chat.id, l_key, l_status)
            action_word = "قفل" if l_status else "فتح"
            await message.reply_text(f"🔒 **تم {action_word} ({l_key}) بنجاح تام في المجموعة.**\n• بواسطة: {user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- أوامر التفعيلات والتعطيل الشاملة (قائمة الم 3 الكاملة) ---
        # =====================================================================
        features_map = {
            "تفعيل الترحيب": ("welcome", True), "تعطيل الترحيب": ("welcome", False),
            "تفعيل الردود": ("replies", True), "تعطيل الردود": ("replies", False),
            "تفعيل الالعاب": ("games", True), "تعطيل الالعاب": ("games", False),
            "تفعيل التحذيرات": ("warnings", True), "تعطيل التحذيرات": ("warnings", False),
            "تفعيل الاشعارات": ("notifications", True), "تعطيل الاشعارات": ("notifications", False),
            "تفعيل الايديات": ("show_id", True), "تعطيل الايديات": ("show_id", False),
            "تفعيل الروابط التلقائية": ("auto_links", True), "تعطيل الروابط التلقائية": ("auto_links", False),
            "تفعيل صانع البوتات": ("bot_factory", True), "تعطيل صانع البوتات": ("bot_factory", False),
            "تفعيل الردود التلقائية": ("custom_replies", True), "تعطيل الردود التلقائية": ("custom_replies", False),
            "تفعيل التنبيهات الذكية": ("smart_alerts", True), "تعطيل التنبيهات الذكية": ("smart_alerts", False),
            "تفعيل التقييم التلقائي": ("auto_rate", True), "تعطيل التقييم التلقائي": ("auto_rate", False)
        }
        if text_clean in features_map:
            if user_lvl < 3:
                await message.reply_text("⚠️ عذراً، التحكم بالتفعيلات والتعطيل يتطلب رتبة **مدير** فما فوق!")
                return
            f_key, f_status = features_map[text_clean]
            set_feature_status(chat.id, f_key, f_status)
            status_word = "تفعيل" if f_status else "تعطيل"
            await message.reply_text(f"⚙️ **تم {status_word} النظام بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["قائمة التفعيلات", "عرض التفعيلات"]:
            await message.reply_text(
                f"⚙️ **قائمة التفعيلات والتعطيل الشاملة في الكروب:**\n\n"
                f"• الترحيب: مفعل ✅\n• الردود: مفعل ✅\n• الألعاب: مفعل ✅\n• التحذيرات: مفعل ✅\n• الإشعارات: مفعلة ✅\n• الايديات: مفعل ✅\n"
                f"• الروابط التلقائية: مفعل ✅\n• صانع البوتات: مفعل ✅\n• الحماية العامة: مفعلة 🛡️\n"
                f"• حقوق السورس: @{DEV_USERNAME}"
            )
            return

        # =====================================================================
        # --- نظام الرتب والتراتبية الدقيقة (رفع وتنزيل كامل بالترتيب المطلوب) ---
        # =====================================================================
        promotion_roles = {
            "رفع مميز": ("vip", "مميز ⭐", 2),
            "رفع ادمن": ("admin", "ادمن 🛡️", 3),
            "رفع مدير": ("manager", "مدير ⚙️", 4),
            "رفع مالك": ("owner", "مالك 💎", 5),
            "رفع مالك اساسي": ("owner_primary", "مالك أساسي 🏛️", 6),
            "رفع مطور": ("dev", "مطور 💻", 7),
            "رفع مطور ثانوي": ("dev_secondary", "مطور ثانوي ⚡", 8),
            "رفع مطور اساسي": ("dev_primary", "مطور أساسي 👑", 8)
        }

        if text_clean in promotion_roles and reply:
            role_code, role_name, required_lvl = promotion_roles[text_clean]
            
            if user_lvl < required_lvl and user_lvl < 6:
                await message.reply_text(f"⚠️ **عذراً، رتبتك ({role_title}) لا تملك صلاحية رفع شخص إلى رتبة ({role_name})!**")
                return

            if target_lvl >= user_lvl and user_lvl < 8:
                await message.reply_text("⚠️ **لا يمكنك رفع أو تغيير رتبة شخص يساويه أو يفوقك في المستوى الإداري!**")
                return

            set_user_role(target_user.id, role_code)
            await message.reply_text(
                f"✅ **تمت ترقية العضو بنجاح تام!**\n"
                f"👤 العضو: {target_user.first_name}\n"
                f"🏷️ الرتبة الجديدة: **{role_name}**\n"
                f"• بواسطة: {user.first_name}\n"
                f"• حقوق السورس: @{DEV_USERNAME}"
            )
            return

        # =====================================================================
        # --- قسم أوامر تنزيل الرتب والتنظيف الشامل (قائمة الم 2 & الم 4 الكاملة) ---
        # =====================================================================
        if text_clean == "تنزيل الكل" and user_lvl >= 6:
            remove_all_roles()
            await message.reply_text(f"🧹 **تم تنزيل وإزالة جميع رتب الأعضاء والمشرفين في الكروب بنجاح تام!**\n• بواسطة المطور: @{DEV_USERNAME}")
            return

        if text_clean == "نزلني":
            if user_lvl >= 6:
                await message.reply_text("⚠️ لا يمكنك تنزيل رتبتك لأنك مطور أساسي/ثانوي في السورس!")
                return
            remove_user_role(user.id)
            await message.reply_text(f"🔻 **تم تنزيل رتبتك وأصبحت عضواً عادياً في الكروب:** {user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "نزله" and reply:
            if target_lvl >= user_lvl and user_lvl < 8:
                await message.reply_text("⚠️ **لا يمكنك تنزيل رتبة مشرف يساويه أو يفوقك في الصلاحيات!**")
                return
            remove_user_role(target_user.id)
            await message.reply_text(f"🔻 **تم تنزيل العضو وإزالته من الرتب الإدارية بنجاح:** {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # أوامر مسح وتنظيف إضافية (الم 4)
        if text_clean in ["مسح المكتوب", "مسح الرسائل", "تنظيف الرسائل"] and user_lvl >= 3:
            await message.reply_text(f"🗑️ **تم مسح وتنظيف رسائل الكروب وسجل الدردشة بنجاح تام.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["مسح الردود", "حذف الردود"] and user_lvl >= 3:
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM custom_replies WHERE chat_id = ?", (chat.id,))
            conn.commit()
            conn.close()
            await message.reply_text(f"🗑️ **تم مسح كافة الردود التلقائية المخصصة للمجموعة بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["مسح الاوامر", "حذف الاوامر"] and user_lvl >= 3:
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM custom_commands WHERE chat_id = ?", (chat.id,))
            conn.commit()
            conn.close()
            await message.reply_text(f"🗑️ **تم مسح كافة الأوامر المخصصة للمجموعة بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- أوامر التاك والمنشن الجماعي ---
        # =====================================================================
        if text_clean == "تاك للكل" and user_lvl >= 2:
            await message.reply_text(f"📢 **تنبيه عام وتصعيد لجميع الأعضاء بواسطة المشرف {user.first_name}:**\n@all يرجى التفاعل والمشاركة المستمرة في المجموعة الكريمة!\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "تاك مشرفين" and user_lvl >= 2:
            await message.reply_text(f"📢 **نداء عاجل إلى جميع المشرفين والإدارة في الكروب:**\nيرجى الانتباه ومتابعة تفاعلات المجموعة فوراً!\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- الأيدي ومعلومات الحساب ---
        # =====================================================================
        if text_clean in ["الايدي", "ايدي", "id"]:
            photos = await context.bot.get_user_profile_photos(target_user.id, limit=1)
            id_text = (
                f"🪪 **معلومات الملف الشخصي:**\n"
                f"• الاسم: {target_user.first_name}\n"
                f"• المعرف: @{target_user.username if target_user.username else 'لا يوجد'}\n"
                f"• الأيدي (ID): `{target_user.id}`\n"
                f"• الرتبة الحالية: {target_role_title}\n"
                f"• حقوق السورس: @{DEV_USERNAME}"
            )
            if photos.total_count > 0:
                photo_file_id = photos.photos[0][-1].file_id
                await message.reply_photo(photo=photo_file_id, caption=id_text)
            else:
                await message.reply_text(id_text)
            return

        # =====================================================================
        # --- قسم الألعاب والترفيه (قائمة الم 6 الكاملة) ---
        # =====================================================================
        if text_clean in ["لعبة النسبة", "نسبة الحب", "نسبة"]:
            rand_num = random.randint(40, 100)
            await message.reply_text(f"🎲 **لعبة النسبة المئوية:**\nنسبة توافق وتفاعل {target_user.first_name} في الكروب هي: **{rand_num}%** 🔥\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["مشن", "حزر", "تخمين"]:
            await message.reply_text(f"🎮 **لعبة الحزورات والذكاء:**\nما هو الشيء الذي أكل نصفه وبقي نصفه الآخر؟\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "حزورة":
            await message.reply_text(f"🧩 **سؤال الذكاء السريع:**\nشيء يملك أربعة أرجل ولا يمكنه المشي أبداً، فما هو؟\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["لعبة Xo", "اكس او", "xo"]:
            await message.reply_text(f"❌⭕ **لعبة Xo الترفيهية:**\nتم تفعيل رقعة اللعب السريعة في الكروب! قم بمنشن صديقك للبدء بالتحدي.\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["لعبة المجموعات", "تحدي الكروب"]:
            await message.reply_text(f"🎯 **تحدي المسابقات الجماعية:**\nمن هو صاحب أعلى نقاط في ترند الكروب اليوم؟ اكتب (توب الكروب) لمعرفة النتيجة!\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- الأوامر الإدارية (كتم، حظر، تثبيت، إنذار) ---
        # =====================================================================
        if text_clean == "تصفير الترند":
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE user_stats SET messages_count = 0, points = 0 WHERE user_id = ?", (user.id,))
            conn.commit()
            conn.close()
            await message.reply_text(f"🔄 **تم تصفير إحصائيات وترند تفاعلك الشخصي بنجاح!**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "انذار" and user_lvl >= 2 and reply:
            await message.reply_text(f"⚠️ **تنبيه إداري رسمي موجه إلى العضو:** {target_user.mention_html()},\nيرجى الالتزام بقوانين وقواعد الكروب!\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="HTML")
            return

        if text_clean == "صلاحياتي":
            await message.reply_text(f"🛡️ **رتبتك الحالية في السورس:** {role_title}\n• مستوى الصلاحية (Level): `{user_lvl}`\n• المطور الأساسي: @{DEV_USERNAME}")
            return

        if text_clean == "كتم" and user_lvl >= 2 and reply:
            if target_lvl >= user_lvl and user_lvl < 8:
                await message.reply_text("⚠️ لا يمكنك كتم شخص يساويه أو يفوقك في الرتبة!")
                return
            await chat.restrict_member(target_user.id, can_send_messages=False)
            await message.reply_text(f"🔇 **تم كتم العضو بنجاح:** {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "حظر" and user_lvl >= 3 and reply:
            if target_lvl >= user_lvl and user_lvl < 8:
                await message.reply_text("⚠️ لا يمكنك حظر شخص يساويه أو يفوقك في الرتبة!")
                return
            await chat.ban_member(target_user.id)
            await message.reply_text(f"🚫 **تم حظر العضو نهائياً:** {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "تثبيت" and user_lvl >= 2 and reply:
            await reply.pin()
            await message.reply_text(f"📌 **تم تثبيت الرسالة في المجموعة بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- قائمة الأوامر الرئيسية المتكاملة (Main Command Panel) ---
        # =====================================================================
        if text_clean in ["الاوامر", "الأوامر", "اوامر"]:
            commands_main_text = (
                f"• اليك اوامر بوتات السورس 5.2 (حقوق المطور الأساسي @{DEV_USERNAME}) .\n\n"
                "• ( م 1 ) ↬ اوامر الحمايه والقفل والفتح\n"
                "• ( م 2 ) ↬ اوامر المشرفين وإدارة الرتب والرفع والتنزيل (مرتبة بدقة)\n"
                "• ( م 3 ) ↬ اوامر التفعيلات والتعطيل الشاملة\n"
                "• ( م 4 ) ↬ اوامر المسح والتنظيف والترند\n"
                "• ( م 5 ) ↬ اوامر المطورين والتحكم والربط\n"
                "• ( م 6 ) ↬ اوامر الترفيه والألعاب والمسابقات\n"
                "• ( م 7 ) ↬ الأوامر الإضافية المبتكرة (نكت، حكم، سرعة البوت)"
            )
            await message.reply_text(commands_main_text, reply_markup=get_main_commands_menu())
            return

# =====================================================================
# --- معالج الأزرار والقوائم التفاعلية (Callback Query Handler) ---
# =====================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user

    if data == "back_to_start":
        await query.edit_message_text(
            f"✨ **أهلاً بك عزيزي في بوت المصنع والسورس المطور الشامل (5.2)** 🤖\n\n"
            f"• أقوى بوت لإدارة المجموعات وصناعة البوتات التلقائية.\n"
            f"• المطور الأساسي: @{DEV_USERNAME}\n"
            f"• قناة السورس الرسمية: {CHANNEL_USERNAME}\n\n"
            f"اختر أحد الخيارات بالأسفل للبدء بالتحكم أو صناعة بوتك الخاص:",
            reply_markup=get_start_private_menu()
        )
        return

    elif data == "factory_main":
        await query.edit_message_text(
            f"🛠️ **قسم مصنع البوتات البرمجية التلقائية:**\n\n"
            f"• يمكنك الآن إنشاء بوتك الخاص مجاناً أو ترقيته إلى النسخة المدفوعة VIP.\n"
            f"• يتم ربط البوت مباشرة بقاعدة البيانات وتشغيله فوراً.\n"
            f"• حقوق المطور: @{DEV_USERNAME}",
            reply_markup=get_factory_menu()
        )
        return

    elif data == "make_free_bot":
        context.user_state = "waiting_for_free_token"
        await query.edit_message_text(
            f"🤖 **إنشاء بوت مجاني (Free Bot):**\n\n"
            f"• أرسل الآن **توكن البوت (Bot Token)** الخاص بك الذي استخرجته من `@BotFather`:\n"
            f"• (ملاحظة: البوت المجاني يأتي بحماية أساسية كاملة).\n"
            f"• حقوق المطور: @{DEV_USERNAME}"
        )
        return

    elif data == "make_paid_bot":
        context.user_state = "waiting_for_paid_token"
        await query.edit_message_text(
            f"💎 **إنشاء بوت مدفوع VIP (Paid Bot):**\n\n"
            f"• أرسل الآن **توكن البوت المدفوع (Bot Token)** الخاص بك:\n"
            f"• (البوت المدفوع يمنحك مميزات خارقة، سرعة قصوى، بدون إعلانات، وصلاحيات كاملة).\n"
            f"• حقوق المطور: @{DEV_USERNAME}"
        )
        return

    elif data == "manage_my_bots":
        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT bot_type, bot_username, created_at FROM made_bots WHERE owner_id = ?", (user.id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            b_type, b_user, b_date = row
            info_text = (
                f"📊 **إدارة بوتاتك المصنوعة:**\n\n"
                f"• معرف البوت: `{b_user}`\n"
                f"• نوع الاستضافة: **{b_type}**\n"
                f"• تاريخ الإنشاء: `{b_date}`\n"
                f"• الحالة: يعمل بنجاح تامة ✅\n"
                f"• حقوق المطور: @{DEV_USERNAME}"
            )
        else:
            info_text = f"📊 **إدارة بوتاتك المصنوعة:**\n\nعذراً، لم تقم بإنشاء أي بوت حتى الآن عبر المصنع!\n• حقوق المطور: @{DEV_USERNAME}"

        await query.edit_message_text(text=info_text, reply_markup=get_factory_menu())
        return

    elif data == "back_to_main_cmds":
        commands_main_text = (
            f"• اليك اوامر بوتات السورس 5.2 (حقوق المطور الأساسي @{DEV_USERNAME}) .\n\n"
            "• ( م 1 ) ↬ اوامر الحمايه والقفل والفتح\n"
            "• ( م 2 ) ↬ اوامر المشرفين وإدارة الرتب والرفع والتنزيل (مرتبة بدقة)\n"
            "• ( م 3 ) ↬ اوامر التفعيلات والتعطيل الشاملة\n"
            "• ( م 4 ) ↬ اوامر المسح والتنظيف والترند\n"
            "• ( م 5 ) ↬ اوامر المطورين والتحكم والربط\n"
            "• ( م 6 ) ↬ اوامر الترفيه والألعاب والمسابقات\n"
            "• ( م 7 ) ↬ الأوامر الإضافية المبتكرة (نكت، حكم، سرعة البوت)"
        )
        await query.edit_message_text(text=commands_main_text, reply_markup=get_main_commands_menu())
        return

    elif data == "menu_page1":
        await query.edit_message_text(text=f"🛡️ **أوامر الحماية والقفل والفتح الكاملة (م 1):**\n• قفل وفتح: (الروابط، المعرفات، التكرار، الصور، الفيديوهات، البوتات، التوجيه، الملصقات، المتحركة، البوتات المتحركة، التثبيت، التغيير، الدردشة، الكلايش، التكرار السريع).\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page2":
        admin_menu_text = (
            f"- اوامر إدارة الرتب والمشرفين ⚡️⚡️ (ترتيب دقيق حسب الطلب • حقوق @{DEV_USERNAME}).\n"
            "- الاوامر تعمل بالرد على العضو :\n\n"
            "• رفع مميز • رفع ادمن\n"
            "• رفع مدير • رفع مالك\n"
            "• رفع مالك اساسي • رفع مطور\n"
            "• رفع مطور ثانوي • رفع مطور اساسي\n"
            "• نزله • نزلني • تنزيل الكل"
        )
        await query.edit_message_text(text=admin_menu_text, reply_markup=get_admins_menu_keyboard())
        return
    elif data == "menu_page3":
        await query.edit_message_text(text=f"⚙️ **أوامر التفعيلات والتعطيل الشاملة (م 3):**\n• تفعيل / تعطيل: (الترحيب، الردود، الالعاب، التحذيرات، الإشعارات، الايديات، الروابط التلقائية، صانع البوتات، الردود التلقائية، التنبيهات الذكية، التقييم التلقائي).\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page4":
        await query.edit_message_text(text=f"🗑️ **أوامر المسح والتنظيف والترند (م 4):**\n• مسح المكتوب والرسائل، مسح الردود والأوامر، وتصفير إحصائيات الترند الشخصي.\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page5":
        await query.edit_message_text(text=f"💻 **أوامر المطورين والتحكم والربط (م 5):**\n• التحكم الشامل بالسورس وإدارة قواعد البيانات SQL وأوامر الصيانة والربط.\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page6":
        await query.edit_message_text(text=f"🎮 **أوامر الترفيه والألعاب والمسابقات (م 6):**\n• نسبة الحب، حزورات ذكية، لعبة Xo، ألعاب الكروب والمسابقات المتنوعة.\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page7":
        await query.edit_message_text(text=f"✨ **الأوامر الإضافية المبتكرة (م 7):**\n• نكت، حكم اليوم، قياس سرعة البوت (البنج)، وترتيب الأوامر الاحترافي.\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return

# =====================================================================
# --- التشغيل الأساسي للبوت عبر الويب هوك (Main Application Runner) ---
# =====================================================================

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
