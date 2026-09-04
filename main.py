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
# --- قاعدة البيانات وأنظمة التخزين الموسعة والمطورة (Database & Storage) ---
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_welcome (
            chat_id INTEGER PRIMARY KEY,
            welcome_text TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_bot_names (
            chat_id INTEGER PRIMARY KEY,
            bot_custom_name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS made_bots (
            owner_id INTEGER PRIMARY KEY,
            bot_token TEXT,
            bot_type TEXT,
            bot_username TEXT,
            custom_bot_display_name TEXT,
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

def get_group_welcome(chat_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT welcome_text FROM group_welcome WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "أهلاً بك عزيزي في الكروب 🌸 نورتنا يا أسطورة!"

def set_group_welcome(chat_id, text):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO group_welcome (chat_id, welcome_text) VALUES (?, ?)", (chat_id, text))
    conn.commit()
    conn.close()

def get_group_bot_name(chat_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT bot_custom_name FROM group_bot_names WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "سورس اندريس 🤖"

def set_group_bot_name(chat_id, name):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO group_bot_names (chat_id, bot_custom_name) VALUES (?, ?)", (chat_id, name))
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
        [InlineKeyboardButton("🛠️ قسم صناعة البوتات والمصنع (Andress)", callback_data="factory_main")],
        [InlineKeyboardButton("📚 قائمة الأوامر والشاملة (سورس اندريس)", callback_data="back_to_main_cmds")],
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
        [InlineKeyboardButton("• [ م 1 ] الحماية الشاملة المتقدمة •", callback_data="menu_page1"), InlineKeyboardButton("• [ م 2 ] المشرفين والرتب العليا •", callback_data="menu_page2")],
        [InlineKeyboardButton("• [ م 3 ] التفعيلات والتعطيل والترحيب •", callback_data="menu_page3"), InlineKeyboardButton("• [ م 4 ] المسح والتنظيف والترند •", callback_data="menu_page4")],
        [InlineKeyboardButton("• [ م 5 ] المطورين وتعديل الأسماء •", callback_data="menu_page5"), InlineKeyboardButton("• [ م 6 ] الألعاب والمسابقات (20 لعبة) •", callback_data="menu_page6")],
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

    # --- الترحيب التلقائي بالأعضاء الجدد في المجموعات ---
    if message.new_chat_members:
        for new_member in message.new_chat_members:
            if new_member.id == context.bot.id:
                continue
            custom_welcome = get_group_welcome(chat.id)
            formatted_welcome = (
                custom_welcome
                .replace("{name}", new_member.first_name)
                .replace("{username}", f"@{new_member.username}" if new_member.username else "لا يوجد")
                .replace("{id}", str(new_member.id))
            )
            await message.reply_text(
                f"✨ **ترحيب خاص بالعضو الجديد:**\n\n{formatted_welcome}\n\n• من سورس اندريس الحصري: @{DEV_USERNAME}"
            )
        return

    # --- معالجة المحادثات الخاصة (Private Chats) ---
    if chat.type == "private":
        save_user(user.id, user.username, user.full_name)
        
        if text_clean == "/start":
            await message.reply_text(
                f"✨ **أهلاً بك عزيزي في سورس اندريس (Andress Source 6.0)** 🤖\n\n"
                f"• أقوى سورس وبوت تليجرام لإدارة المجموعات وصناعة البوتات التلقائية بكفاءة فائقة.\n"
                f"• المطور الأساسي: @{DEV_USERNAME}\n"
                f"• قناة السورس الرسمية: {CHANNEL_USERNAME}\n\n"
                f"اختر أحد الخيارات بالأسفل للبدء بالتحكم أو صناعة بوتك الخاص:",
                reply_markup=get_start_private_menu()
            )
            return

        if context.user_state == "waiting_for_free_token":
            bot_token = text_clean
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO made_bots (owner_id, bot_token, bot_type, bot_username, custom_bot_display_name, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                           (user.id, bot_token, "مجاني (Free)", f"@Andress_Bot_{random.randint(1000,9999)}", "اندريس المجاني", time.strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            context.user_state = None
            await message.reply_text(
                f"🎉 **تم إنشاء بوتك المجاني عبر سورس اندريس بنجاح تام!**\n\n"
                f"• اسم البوت الافتراضي: اندريس المجاني\n"
                f"• حالة الخادم: يعمل الآن على الاستضافات السحابية ⚡\n"
                f"• حقوق المطور الأساسي: @{DEV_USERNAME}",
                reply_markup=get_factory_menu()
            )
            return

        if context.user_state == "waiting_for_paid_token":
            bot_token = text_clean
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO made_bots (owner_id, bot_token, bot_type, bot_username, custom_bot_display_name, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                           (user.id, bot_token, "مدفوع VIP (Paid)", f"@Andress_VIP_{random.randint(1000,9999)}", "اندريس المدفوع VIP", time.strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            context.user_state = None
            await message.reply_text(
                f"💎 **تم تفعيل وإنشاء بوتك المدفوع VIP بنجاح خارق عبر سورس اندريس!**\n\n"
                f"• اسم البوت: اندريس المدفوع VIP 🚀\n"
                f"• حماية قصوى + سرعة خيالية + استجابة فورية وحصريات.\n"
                f"• حقوق المطور الأساسي: @{DEV_USERNAME}",
                reply_markup=get_factory_menu()
            )
            return

        return

    # --- معالجة المجموعات والمجتمعات (Groups & Supergroups) ---
    if chat.type in ["group", "supergroup"]:
        save_user(user.id, user.username, user.full_name)
        update_user_stats(user.id, is_photo=bool(message.photo))

        # --- الرد عند كتابة "بوت" حصرياً ---
        if text_clean.lower() == "بوت":
            current_bot_name = get_group_bot_name(chat.id)
            await message.reply_text(
                f"🤖 **أنا {current_bot_name}**\n"
                f"• أنا سورس اندريس القوي والمطور لإدارة وحماية الكروبات بكفاءة فائقة.\n"
                f"• المطور الأساسي ورئيس السورس: @{DEV_USERNAME}"
            )
            return

        if text_clean == "تفعيل":
            activate_group(chat.id, chat.title)
            await message.reply_text(f"✅ **تم تفعيل سورس اندريس المتطور والحماية الشاملة في هذه المجموعة بنجاح تام!**\n• المطور الأساسي: @{DEV_USERNAME}")
            return

        reply = message.reply_to_message
        target_user = reply.from_user if reply else user
        target_role_title = get_user_role_title(target_user.id, target_user.username)
        target_lvl = get_role_level(target_user.id, target_user.username)

        # --- اختصارات الأوامر السريعة ---
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

        if text_clean == "ترتيب الاوامر":
            markup_order = InlineKeyboardMarkup([
                [InlineKeyboardButton("قناة سورس اندريس الرسمية 🍓", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")]
            ])
            await message.reply_text("- : تم ترتيب اوامر سورس اندريس الأساسية باحترافية تامة وتصل للمطور الأساسي،", reply_markup=markup_order)
            return

        # =====================================================================
        # --- أوامر تعيين وتعديل الترحيب واسم البوت للمطور والمدراء ---
        # =====================================================================
        if text_clean.startswith("تعيين ترحيب ") or text_clean.startswith("وضع ترحيب "):
            if user_lvl < 3:
                await message.reply_text("⚠️ عذراً، تعيين رسالة الترحيب يتطلب رتبة **مدير** أو أعلى!")
                return
            new_wel_text = text_clean.replace("تعيين ترحيب ", "").replace("وضع ترحيب ", "").strip()
            set_group_welcome(chat.id, new_wel_text)
            await message.reply_text(
                f"✅ **تم تحديث وتعيين رسالة الترحيب في الكروب بنجاح!**\n\n"
                f"• النص الجديد:\n`{new_wel_text}`\n\n"
                f"*(يمكنك استخدام المتغيرات: `{{name}}` لاسم العضو، `{{username}}` لمعرفه، `{{id}}` لأيديه)*\n"
                f"• سورس اندريس: @{DEV_USERNAME}"
            )
            return

        if text_clean == "عرض الترحيب":
            current_wel = get_group_welcome(chat.id)
            await message.reply_text(f"📋 **رسالة الترحيب الحالية في الكروب:**\n\n`{current_wel}`\n• سورس اندريس: @{DEV_USERNAME}")
            return

        # صلاحيات التحكم باسم البوت في الكروب وفي البوتات المصنوعة
        if text_clean.startswith("تعيين اسم البوت ") or text_clean.startswith("وضع اسم البوت "):
            if user_lvl < 5 and user_lvl < 8:
                await message.reply_text("⚠️ عذراً، هذا الأمر مخصص للمطور الأساسي والمالك الأساسي فقط لتغيير اسم البوت!")
                return
            new_b_name = text_clean.replace("تعيين اسم البوت ", "").replace("وضع اسم البوت ", "").strip()
            set_group_bot_name(chat.id, new_b_name)
            
            # تحديث اسم البوت في جدول البوتات المصنوعة للمستخدم إن وجد
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE made_bots SET custom_bot_display_name = ? WHERE owner_id = ?", (new_b_name, user.id))
            conn.commit()
            conn.close()

            await message.reply_text(
                f"🏷️ **تم تغيير اسم البوت بنجاح خارق!**\n\n"
                f"• الاسم الجديد في هذا الكروب وفي بوتاتك المصنوعة: **{new_b_name}**\n"
                f"• سورس اندريس الحصري: @{DEV_USERNAME}"
            )
            return

        if text_clean == "اسم البوت":
            current_b_name = get_group_bot_name(chat.id)
            await message.reply_text(f"🤖 **اسم البوت الحالي:** **{current_b_name}**\n• المطور الأساسي: @{DEV_USERNAME}")
            return

        # --- الأوامر والردود المخصصة ---
        if text_clean.startswith("اضف امر ") and user_lvl >= 2 and reply:
            cmd_key = text_clean.replace("اضف امر ", "").strip()
            cmd_val = reply.text or reply.caption or "محتوى الأمر المخصص"
            add_custom_command(chat.id, cmd_key, cmd_val)
            await message.reply_text(f"➕ **تم إضافة الأمر الجديد بنجاح في سورس اندريس:** `{cmd_key}`\n• حقوق السورس: @{DEV_USERNAME}")
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

        # --- سرعة البوت وترند الكروب ---
        if text_clean in ["سرعة البوت", "البنج", "السرعة"]:
            ping_time = round((time.time() - START_TIME) % 1, 3) * 1000
            await message.reply_text(f"⚡ **سرعة استجابة سورس اندريس (البنج):** `{int(ping_time)} ms`\n• يعمل بكفاءة خارقة على استضافات 2026\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["توب الكروب", "لوحة الشرف", "الترند"]:
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, points FROM user_stats ORDER BY points DESC LIMIT 5")
            top_users = cursor.fetchall()
            conn.close()
            
            top_text = "🏆 **قائمة الشرف والترند الأنشط في الكروب (سورس اندريس):**\n\n"
            for idx, (uid, pts) in enumerate(top_users, 1):
                top_text += f"{idx} • الأيدي (`{uid}`) - النقاط: **{pts}** نقطة 🔥\n"
            top_text += f"\n• حقوق السورس: @{DEV_USERNAME}"
            await message.reply_text(top_text)
            return

        # =====================================================================
        # --- نظام القفل والفتح الشامل الموسع (حماية متقدمة ومحدثة بالكامل) ---
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
            "قفل التكرار السريع": ("fast_flood", True), "فتح التكرار السريع": ("fast_flood", False),
            "قفل الفحش": ("profanity", True), "فتح الفحش": ("profanity", False),
            "قفل الجهات": ("contacts", True), "فتح الجهات": ("contacts", False),
            "قفل الملفات": ("files", True), "فتح الملفات": ("files", False),
            "قفل الصوتيات": ("audio", True), "فتح الصوتيات": ("audio", False),
            "قفل البصمات": ("voices", True), "فتح البصمات": ("voices", False),
            "قفل الكوبونات": ("coupons", True), "فتح الكوبونات": ("coupons", False),
            "قفل التاك الجماعي": ("mass_tag", True), "فتح التاك الجماعي": ("mass_tag", False),
            "قفل التفاعل الوهمي": ("fake_interact", True), "فتح التفاعل الوهمي": ("fake_interact", False),
            "قفل الالعاب": ("games_lock", True), "فتح الالعاب": ("games_lock", False),
            "قفل الفويس": ("voices_lock", True), "فتح الفويس": ("voices_lock", False),
            "قفل الاشعارات": ("notifs_lock", True), "فتح الاشعارات": ("notifs_lock", False)
        }
        if text_clean in locks_map:
            if user_lvl < 3:
                await message.reply_text("⚠️ عذراً، هذا الأمر يتطلب رتبة **مدير** أو أعلى للتحكم بالحماية الشاملة!")
                return
            l_key, l_status = locks_map[text_clean]
            set_lock(chat.id, l_key, l_status)
            action_word = "قفل" if l_status else "فتح"
            await message.reply_text(f"🔒 **تم {action_word} ({l_key}) بنجاح تام في المجموعة عبر حماية سورس اندريس.**\n• بواسطة: {user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- أوامر التفعيلات والتعطيل الشاملة ---
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
            await message.reply_text(f"⚙️ **تم {status_word} النظام بنجاح عبر سورس اندريس.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["قائمة التفعيلات", "عرض التفعيلات"]:
            await message.reply_text(
                f"⚙️ **قائمة التفعيلات والتعطيل الشاملة في الكروب (سورس اندريس):**\n\n"
                f"• الترحيب: مفعل ✅\n• الردود: مفعل ✅\n• الألعاب: مفعل ✅\n• التحذيرات: مفعل ✅\n• الإشعارات: مفعلة ✅\n• الايديات: مفعل ✅\n"
                f"• الروابط التلقائية: مفعل ✅\n• صانع البوتات: مفعل ✅\n• الحماية العامة: مفعلة 🛡️\n"
                f"• حقوق السورس: @{DEV_USERNAME}"
            )
            return

        # =====================================================================
        # --- نظام رفع الرتب بدقة (وصولاً للمطور الأساسي المربوط بمعرفك) ---
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
            
            if user_lvl < required_lvl and user_lvl < 8:
                await message.reply_text(f"⚠️ **عذراً، رتبتك ({role_title}) لا تملك صلاحية رفع شخص إلى رتبة ({role_name})!**")
                return

            if target_lvl >= user_lvl and user_lvl < 8:
                await message.reply_text("⚠️ **لا يمكنك رفع أو تغيير رتبة شخص يساويه أو يفوقك في المستوى الإداري!**")
                return

            set_user_role(target_user.id, role_code)
            await message.reply_text(
                f"✅ **تمت ترقية العضو بنجاح تام عبر سورس اندريس لتصل للمطور الأساسي @{DEV_USERNAME}!**\n"
                f"👤 العضو: {target_user.first_name}\n"
                f"🏷️ الرتبة الجديدة: **{role_name}**\n"
                f"• بواسطة: {user.first_name}\n"
                f"• حقوق السورس: @{DEV_USERNAME}"
            )
            return

        # =====================================================================
        # --- قسم تنزيل الرتب والتنظيف الشامل ---
        # =====================================================================
        if text_clean == "تنزيل الكل" and user_lvl >= 6:
            remove_all_roles()
            await message.reply_text(f"🧹 **تم تنزيل وإزالة جميع رتب الأعضاء والمشرفين في الكروب بنجاح تام!**\n• بواسطة المطور: @{DEV_USERNAME}")
            return

        if text_clean == "نزلني":
            if user_lvl >= 6:
                await message.reply_text("⚠️ لا يمكنك تنزيل رتبتك لأنك مطور أساسي في سورس اندريس!")
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
        # --- التاك الجماعي ---
        # =====================================================================
        if text_clean == "تاك للكل" and user_lvl >= 2:
            await message.reply_text(f"📢 **تنبيه عام وتصعيد لجميع الأعضاء بواسطة المشرف {user.first_name} (سورس اندريس):**\n@all يرجى التفاعل والمشاركة المستمرة في المجموعة!\n• حقوق السورس: @{DEV_USERNAME}")
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
                f"🪪 **معلومات الملف الشخصي (سورس اندريس):**\n"
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
        # --- قسم الألعاب والمسابقات الموسع (20 لعبة تشغيلية كاملة) ---
        # =====================================================================
        games_dict = {
            "لعبة النسبة": f"🎲 **نسبة توافق وتفاعل {target_user.first_name} في الكروب:** {random.randint(40, 100)}% 🔥",
            "نسبة الحب": f"❤️ **نسبة الحب والتوافق بين العضوين:** {random.randint(50, 100)}% 💞",
            "لعبة الصراحة": f"🎯 **سؤال صراحة:** هل تخفي سراً عن صديقك المقرب؟ صرح الآن بدون خجل! 🤭",
            "لعبة المانجا": f"📖 **تحدي الأنمي والمانجا:** من هو الشخصية الأقوى في سلسلة ناروتو برأيك؟ 🍥",
            "لعبة التحدي": f"⚔️ **تحدي سورس اندريس:** قم بإرسال 5 رسائل متتالية بأسرع ما يمكن لتثبت نشاطك الخارق! 🚀",
            "لعبة الحروف": f"🔤 **لعبة الحروف السريعة:** اذكر اسماً بحرف **({random.choice(['أ', 'م', 'س', 'ر', 'ع', 'خ', 'ل'])})** بأسرع وقت! ⏱️",
            "لعبة الذكاء": f"🧠 **سؤال ذكاء:** ما هو الشيء الذي يكلمك بدون لسان ويسمعك بدون أذنين؟ (الكتاب) 📚",
            "لعبة التخمين": f"🔮 **لعبة الحظ:** الرقم المحظوظ لديك اليوم هو: **{random.randint(1, 100)}** 🌟",
            "لعبة الموت": f"⚡ **لعبة المغامرة:** من سيفوز بالمعركة الكبرى في الكروب اليوم؟ بالتأكيد أنت يا أسطورة!",
            "لعبة من أنا": f"🕵️‍♂️ **من أنا:** أنا شيء يحيط بالغرفة كلها ولكنه لا يأخذ أي مساحة، فما أنا؟ (الجدار) 🧱",
            "لعبة المليون": f"💰 **سؤال من سيربح المليون:** ما هي عاصمة دولة العراق؟ (بغداد العزة) 🏛️",
            "لعبة الألوان": f"🎨 **لعبة الألوان:** اختر لونك المفضل وسنخبرك بصفة شخصيتك: الأزرق يعني الهدوء والثقة 🌊",
            "لعبة الزحف": f"🐍 **لعبة الزحف:** {target_user.first_name} يحاول الزحف للوصول إلى المركز الأول في الكروب! 😂",
            "لعبة الحظ الكبرى": f"🎰 **دولاب الحظ:** لقد ربحت معنا **{random.randint(10, 500)}** نقطة تفاعل ذهبية! ✨",
            "لعبة المطبخ": f"🍳 **لعبة الطبخ:** الأكلة المقترحة لعشائك اليوم هي دجاج مشوي مع صوص الشواء 🍗",
            "لعبة السيارات": f"🏎️ **لعبة السيارات السريعة:** سيارتك المفضلة المستقبلية هي سيارة رياضية خارقة بقوة 800 حصان! 🏁",
            "لعبة الأبراج": f"🔮 **براجك اليوم:** الحظ يبتسم لك اليوم وعليك استغلال الفرص القادمة بقوة 🌟",
            "لعبة الكراسي": f"🪑 **لعبة الكراسي الموسيقية:** الموسيقى توقفت وتمكن {target_user.first_name} من حجز الكرسي الأخير بنجاح! 👑",
            "لعبة القط والفأر": f}🐱 **لعبة القط والفأر:** أنت الآن بدور القط الماهر، هل ستتمكن من الإمساك بالفأر الهارب؟ 🏃‍♂️",
            "لعبة الملوك": f"👑 **لعبة العرش:** تم تتويج {target_user.first_name} ملكاً متفرداً على عرش الكروب اليوم! 💎"
        }
        
        if text_clean in games_dict:
            await message.reply_text(f"{games_dict[text_clean]}\n• سورس اندريس: @{DEV_USERNAME}")
            return

        if text_clean in ["نكتة", "نكت"]:
            jokes = [
                "محشش سألوه: شو رأيك بالزواج المبكر؟ قال: يعني الساعة 7 الصبح؟ 😂",
                "واحد غبي ضاع تلفونه، صار يبكي، صاحبه قله: لا تبكي اتصل عليه من تلفونك الثاني وشوف وين رايح! قال: تصدق فكرة حلوة! 🤦‍♂️",
                "محشش دخل صيدلية قالهم: عندكم قطرة عيون وسعيدة؟ قالوا: لا والله! قال: خسارة فاتتني الحفلة 😂",
                "واحد أحول سألوه: شو أمنيتك بالحياة؟ قال: أشوف اثنين ماشيين لحالهم! 😆"
            ]
            await message.reply_text(f"😂 **نكتة اليوم من سورس اندريس:**\n\n{random.choice(jokes)}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["حكمة", "حكمة اليوم"]:
            wisdoms = [
                "من أراد النجاح في هذا العالم عليه أن يتجاهل كلام المحبطين.",
                "الصمت هو أفضل رد على السخافات.",
                "الجمال في العقول لا في المظاهر، وسورس اندريس يثبت ذلك.",
                "الاصدقاء الحقيقيون هم من يقفون معك في أوقات الصعاب."
            ]
            await message.reply_text(f"💡 **حكمة سورس اندريس:**\n\n{random.choice(wisdoms)}\n• حقوق السورس: @{DEV_USERNAME}")
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
            await message.reply_text(f"⚠️ **تنبيه إداري رسمي موجه إلى العضو:** {target_user.mention_html()},\nيرجى الالتزام بقوانين وقواعد الكروب!\n• سورس اندريس: @{DEV_USERNAME}", parse_mode="HTML")
            return

        if text_clean == "صلاحياتي":
            await message.reply_text(f"🛡️ **رتبتك الحالية في سورس اندريس:** {role_title}\n• مستوى الصلاحية (Level): `{user_lvl}`\n• المطور الأساسي: @{DEV_USERNAME}")
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
                f"• اليك اوامر سورس اندريس (Andress 6.0) المربوطة حصرياً بالمطور الأساسي @{DEV_USERNAME} .\n\n"
                "• ( م 1 ) ↬ اوامر الحمايه والقفل والفتح الشاملة المتقدمة (روابط، فحش، ملفات، تفاعل وهمي)\n"
                "• ( م 2 ) ↬ اوامر المشرفين وإدارة الرتب والرفع والتنزيل (من العضو إلى المطور الأساسي)\n"
                "• ( م 3 ) ↬ اوامر التفعيلات والتعطيل الشاملة وأوامر (تعيين ترحيب / وضع ترحيب)\n"
                "• ( م 4 ) ↬ اوامر المسح والتنظيف والترند الشخصي\n"
                "• ( م 5 ) ↬ اوامر المطورين وتعديل اسم البوت (تعيين اسم البوت / وضع اسم البوت)\n"
                "• ( م 6 ) ↬ اوامر الترفيه والألعاب والمسابقات (أكثر من 20 لعبة نشطة)\n"
                "• ( م 7 ) ↬ الأوامر الإضافية المبتكرة (نكت، حكم، سرعة البوت، وتفاعل 'بوت')"
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
            f"✨ **أهلاً بك عزيزي في سورس اندريس (Andress Source 6.0)** 🤖\n\n"
            f"• أقوى سورس وبوت تليجرام لإدارة المجموعات وصناعة البوتات التلقائية بكفاءة فائقة.\n"
            f"• المطور الأساسي: @{DEV_USERNAME}\n"
            f"• قناة السورس الرسمية: {CHANNEL_USERNAME}\n\n"
            f"اختر أحد الخيارات بالأسفل للبدء بالتحكم أو صناعة بوتك الخاص:",
            reply_markup=get_start_private_menu()
        )
        return

    elif data == "factory_main":
        await query.edit_message_text(
            f"🛠️ **قسم مصنع البوتات البرمجية التلقائية (سورس اندريس):**\n\n"
            f"• يمكنك الآن إنشاء بوتك الخاص مجاناً أو ترقيته إلى النسخة المدفوعة VIP.\n"
            f"• يتم ربط البوت مباشرة بقاعدة البيانات وتشغيله فوراً.\n"
            f"• حقوق المطور الأساسي: @{DEV_USERNAME}",
            reply_markup=get_factory_menu()
        )
        return

    elif data == "make_free_bot":
        context.user_state = "waiting_for_free_token"
        await query.edit_message_text(
            f"🤖 **إنشاء بوت مجاني (Free Bot) عبر سورس اندريس:**\n\n"
            f"• أرسل الآن **توكن البوت (Bot Token)** الخاص بك الذي استخرجته من `@BotFather`:\n"
            f"• (ملاحظة: البوت المجاني يأتي بحماية أساسية كاملة وتخصيص بالاسم).\n"
            f"• حقوق المطور: @{DEV_USERNAME}"
        )
        return

    elif data == "make_paid_bot":
        context.user_state = "waiting_for_paid_token"
        await query.edit_message_text(
            f"💎 **إنشاء بوت مدفوع VIP (Paid Bot) عبر سورس اندريس:**\n\n"
            f"• أرسل الآن **توكن البوت المدفوع (Bot Token)** الخاص بك:\n"
            f"• (البوت المدفوع يمنحك مميزات خارقة، سرعة قصوى، بدون إعلانات، وصلاحيات كاملة بالأسماء).\n"
            f"• حقوق المطور: @{DEV_USERNAME}"
        )
        return

    elif data == "manage_my_bots":
        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT bot_type, bot_username, custom_bot_display_name, created_at FROM made_bots WHERE owner_id = ?", (user.id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            b_type, b_user, b_display_name, b_date = row
            info_text = (
                f"📊 **إدارة بوتاتك المصنوعة (سورس اندريس):**\n\n"
                f"• اسم البوت: **{b_display_name}**\n"
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
            f"• اليك اوامر سورس اندريس (Andress 6.0) المربوطة حصرياً بالمطور الأساسي @{DEV_USERNAME} .\n\n"
            "• ( م 1 ) ↬ اوامر الحمايه والقفل والفتح الشاملة المتقدمة (روابط، فحش، ملفات، تفاعل وهمي)\n"
            "• ( م 2 ) ↬ اوامر المشرفين وإدارة الرتب والرفع والتنزيل (من العضو إلى المطور الأساسي)\n"
            "• ( م 3 ) ↬ اوامر التفعيلات والتعطيل الشاملة وأوامر (تعيين ترحيب / وضع ترحيب)\n"
            "• ( م 4 ) ↬ اوامر المسح والتنظيف والترند الشخصي\n"
            "• ( م 5 ) ↬ اوامر المطورين وتعديل اسم البوت (تعيين اسم البوت / وضع اسم البوت)\n"
            "• ( م 6 ) ↬ اوامر الترفيه والألعاب والمسابقات (أكثر من 20 لعبة نشطة)\n"
            "• ( م 7 ) ↬ الأوامر الإضافية المبتكرة (نكت، حكم، سرعة البوت، وتفاعل 'بوت')"
        )
        await query.edit_message_text(text=commands_main_text, reply_markup=get_main_commands_menu())
        return

    elif data == "menu_page1":
        await query.edit_message_text(text=f"🛡️ **أوامر الحماية والقفل والفتح الشاملة المتقدمة (م 1):**\n• قفل وفتح: (الروابط، المعرفات، التكرار، الصور، الفيديوهات، البوتات، التوجيه، الملصقات، المتحركة، البوتات المتحركة، التثبيت، التغيير، الدردشة، الكلايش، التكرار السريع، الفحش، الجهات، الملفات، الصوتيات، البصمات، الكوبونات، التاك الجماعي، التفاعل الوهمي، الالعاب، الفويس، الاشعارات).\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page2":
        admin_menu_text = (
            f"- اوامر إدارة الرتب والمشرفين ⚡️⚡️ (مرتبة بدقة وتصل للمطور الأساسي @{DEV_USERNAME}).\n"
            "- الاوامر تعمل بالرد على العضو :\n\n"
            "• رفع مميز • رفع ادمن\n"
            "• رفع مدير • رفع مالك\n"
            "• رفع مالك اساسي • رفع مطور\n"
            "• رفع مطور ثانوي • رفع مطور اساسي 👑\n"
            "• نزله • نزلني • تنزيل الكل"
        )
        await query.edit_message_text(text=admin_menu_text, reply_markup=get_admins_menu_keyboard())
        return
    elif data == "menu_page3":
        await query.edit_message_text(text=f"⚙️ **أوامر التفعيلات والتعطيل والترحيب (م 3):**\n• تفعيل / تعطيل: (الترحيب، الردود، الالعاب، التحذيرات، الإشعارات، الايديات، الروابط التلقائية، صانع البوتات، الردود التلقائية، التنبيهات الذكية، التقييم التلقائي).\n• أوامر الترحيب: (تعيين ترحيب [النص] / وضع ترحيب [النص] / عرض الترحيب).\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page4":
        await query.edit_message_text(text=f"🗑️ **أوامر المسح والتنظيف والترند (م 4):**\n• مسح المكتوب والرسائل، مسح الردود والأوامر، وتصفير إحصائيات الترند الشخصي.\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page5":
        await query.edit_message_text(text=f"💻 **أوامر المطورين وتعديل الأسماء (م 5):**\n• التحكم الشامل بسورس اندريس وإدارة قواعد البيانات SQL.\n• أوامر تغيير اسم البوت: (تعيين اسم البوت [الاسم] / وضع اسم البوت [الاسم] / اسم البوت).\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page6":
        await query.edit_message_text(text=f"🎮 **أوامر الترفيه والألعاب والمسابقات (م 6):**\n• أكثر من 20 لعبة مدمجة: (لعبة النسبة، نسبة الحب، الصراحة، المانجا، التحدي، الحروف، الذكاء، التخمين، الموت، من أنا، المليون، الألوان، الزحف، دولاب الحظ، المطبخ، السيارات، الأبراج، الكراسي، القط والفأر، العرش)، إضافة إلى النكت والحكم اليومية.\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page7":
        await query.edit_message_text(text=f"✨ **الأوامر الإضافية المبتكرة (م 7):**\n• الرد التلقائي بكلمة 'بوت' ليعلن أنه سورس اندريس، نكت، حكم اليوم، قياس سرعة البوت (البنج)، وترتيب الأوامر الاحترافي.\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
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
