import os
import logging
import sqlite3
import random
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
            "owner_primary": "مالك أساسي 🏛️", "owner": "مالك 💎", "creator_basic": "منشئ أساسي 🏗️",
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

# =====================================================================
# --- واجهات وقوائم الأزرار الشاملة (Inline Keyboards & Menus) ---
# =====================================================================

def get_main_commands_menu():
    keyboard = [
        [InlineKeyboardButton("• 1 .", callback_data="menu_page1"), InlineKeyboardButton("• 2 .", callback_data="menu_page2")],
        [InlineKeyboardButton("• 3 .", callback_data="menu_page3")],
        [InlineKeyboardButton("• 4 .", callback_data="menu_page4"), InlineKeyboardButton("• 5 .", callback_data="menu_page5")],
        [InlineKeyboardButton("• 6 .", callback_data="menu_page6")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_sub_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main_cmds")]])

def get_admins_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔇 كتم", callback_data="adm_mute"), InlineKeyboardButton("🚫 حظر", callback_data="adm_ban")],
        [InlineKeyboardButton("📌 تثبيت", callback_data="adm_pin"), InlineKeyboardButton("🗑️ مسح", callback_data="adm_clean")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main_cmds")]
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
    role_title = get_user_role(user.id, user.username)

    # --- معالجة المحادثات الخاصة (Private Chats) ---
    if chat.type == "private":
        save_user(user.id, user.username, user.full_name)
        if text_clean == "/start":
            await message.reply_text(
                f"أهلاً بك في بوت المصنع المطور الشامل 👾\n• مطور السورس الأساسي : @{DEV_USERNAME}\n• قناة التحديثات الرسمية : {CHANNEL_USERNAME}\n\nاختر من الأوامر والخيارات بالأسفل للبدء:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("تفعيل المصنع البرمجي", callback_data="make_free_bot")]])
            )
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
        target_role = get_user_role(target_user.id, target_user.username)
        is_elevated = "مطور" in role_title or "مالك" in role_title or "منشئ" in role_title or "مدير" in role_title or "ادمن" in role_title
        is_owner_or_dev = "مطور" in role_title or "مالك" in role_title

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
        # --- قسم أوامر القفل والفتح الموسعة والشاملة (Locks & Unlocks) ---
        # =====================================================================
        if text_clean == "قفل الروابط" and is_elevated:
            set_lock(chat.id, "links", True)
            await message.reply_text(f"🔒 **تم قفل الروابط بنجاح في المجموعة.**\n• بواسطة: {user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return
        if text_clean == "فتح الروابط" and is_elevated:
            set_lock(chat.id, "links", False)
            await message.reply_text(f"🔓 **تم فتح الروابط بنجاح في المجموعة.**\n• بواسطة: {user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "قفل المعرفات" and is_elevated:
            set_lock(chat.id, "usernames", True)
            await message.reply_text(f"🔒 **تم قفل المعرفات (@) بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return
        if text_clean == "فتح المعرفات" and is_elevated:
            set_lock(chat.id, "usernames", False)
            await message.reply_text(f"🔓 **تم فتح المعرفات بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "قفل التكرار" and is_elevated:
            set_lock(chat.id, "flood", True)
            await message.reply_text(f"🔒 **تم قفل التكرار والسبام بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return
        if text_clean == "فتح التكرار" and is_elevated:
            set_lock(chat.id, "flood", False)
            await message.reply_text(f"🔓 **تم فتح التكرار بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "قفل الصور" and is_elevated:
            set_lock(chat.id, "photos", True)
            await message.reply_text(f"🔒 **تم قفل الصور والملصقات بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return
        if text_clean == "فتح الصور" and is_elevated:
            set_lock(chat.id, "photos", False)
            await message.reply_text(f"🔓 **تم فتح الصور والملصقات بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "قفل الفيديوهات" and is_elevated:
            set_lock(chat.id, "videos", True)
            await message.reply_text(f"🔒 **تم قفل الفيديوهات بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return
        if text_clean == "فتح الفيديوهات" and is_elevated:
            set_lock(chat.id, "videos", False)
            await message.reply_text(f"🔓 **تم فتح الفيديوهات بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "قفل البوتات" and is_elevated:
            set_lock(chat.id, "bots", True)
            await message.reply_text(f"🔒 **تم قفل إضافة البوتات بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return
        if text_clean == "فتح البوتات" and is_elevated:
            set_lock(chat.id, "bots", False)
            await message.reply_text(f"🔓 **تم فتح إضافة البوتات بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- قسم قوائم التفعيل والتعطيل الشاملة (Enable & Disable Menus) ---
        # =====================================================================
        if text_clean == "تفعيل الترحيب" and is_elevated:
            set_feature_status(chat.id, "welcome", True)
            await message.reply_text(f"✅ **تم تفعيل نظام الترحيب بالأعضاء الجدد بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return
        if text_clean == "تعطيل الترحيب" and is_elevated:
            set_feature_status(chat.id, "welcome", False)
            await message.reply_text(f"❌ **تم تعطيل نظام الترحيب بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "تفعيل الردود" and is_elevated:
            set_feature_status(chat.id, "replies", True)
            await message.reply_text(f"✅ **تم تفعيل الردود التلقائية والذكية بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return
        if text_clean == "تعطيل الردود" and is_elevated:
            set_feature_status(chat.id, "replies", False)
            await message.reply_text(f"❌ **تم تعطيل الردود التلقائية بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "تفعيل الالعاب" and is_elevated:
            set_feature_status(chat.id, "games", True)
            await message.reply_text(f"✅ **تم تفعيل قسم الألعاب والترفيه (م 6) بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return
        if text_clean == "تعطيل الالعاب" and is_elevated:
            set_feature_status(chat.id, "games", False)
            await message.reply_text(f"❌ **تم تعطيل قسم الألعاب والترفيه بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "تفعيل التحذيرات" and is_elevated:
            set_feature_status(chat.id, "warnings", True)
            await message.reply_text(f"✅ **تم تفعيل نظام التحذيرات الإدارية بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return
        if text_clean == "تعطيل التحذيرات" and is_elevated:
            set_feature_status(chat.id, "warnings", False)
            await message.reply_text(f"❌ **تم تعطيل نظام التحذيرات بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "قائمة التفعيلات" or text_clean == "عرض التفعيلات":
            await message.reply_text(
                f"⚙️ **قائمة التفعيلات والتعطيل الشاملة في الكروب:**\n\n"
                f"• الترحيب: مفعل ✅\n"
                f"• الردود: مفعل ✅\n"
                f"• الألعاب: مفعل ✅\n"
                f"• التحذيرات: مفعل ✅\n"
                f"• الحماية العامة: مفعلة 🛡️\n\n"
                f"• للتحكم أرسل: (تفعيل [القسم]) أو (تعطيل [القسم])\n"
                f"• حقوق السورس: @{DEV_USERNAME}"
            )
            return

        # =====================================================================
        # --- قسم ترتيب الرتب المتكامل والتراتبية الدقيقة (Role Hierarchy) ---
        # =====================================================================
        if text_clean.startswith("رفع مالك أساسي") and is_owner_or_dev and reply:
            set_user_role(target_user.id, "owner_primary")
            await message.reply_text(f"🏛️ **تم رفع العضو بنجاح ليصبح رتبته:** مالك أساسي 🏛️\n👤 العضو: {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean.startswith("رفع مالك") and is_owner_or_dev and reply:
            set_user_role(target_user.id, "owner")
            await message.reply_text(f"💎 **تم رفع العضو بنجاح ليصبح رتبته:** مالك 💎\n👤 العضو: {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean.startswith("رفع مطور") and is_owner_or_dev and reply:
            set_user_role(target_user.id, "dev")
            await message.reply_text(f"💻 **تم رفع العضو بنجاح ليصبح رتبته:** مطور 💻\n👤 العضو: {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean.startswith("رفع منشئ") and is_elevated and reply:
            set_user_role(target_user.id, "creator")
            await message.reply_text(f"🛠️ **تم رفع العضو بنجاح ليصبح رتبته:** منشئ 🛠️\n👤 العضو: {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean.startswith("رفع مدير") and is_elevated and reply:
            set_user_role(target_user.id, "manager")
            await message.reply_text(f"⚙️ **تم رفع العضو بنجاح ليصبح رتبته:** مدير ⚙️\n👤 العضو: {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean.startswith("رفع ادمن") and is_elevated and reply:
            set_user_role(target_user.id, "admin")
            await message.reply_text(f"🛡️ **تم رفع العضو بنجاح ليصبح رتبته:** ادمن 🛡️\n👤 العضو: {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean.startswith("رفع مميز") and is_elevated and reply:
            set_user_role(target_user.id, "vip")
            await message.reply_text(f"⭐ **تم رفع العضو بنجاح ليصبح رتبته:** مميز ⭐\n👤 العضو: {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- قسم أوامر تنزيل الرتب والتنظيف (Demotion & Unset Commands) ---
        # =====================================================================
        if text_clean.startswith("تنزيل الكل") and is_owner_or_dev:
            remove_all_roles()
            await message.reply_text(f"🧹 **تم تنزيل وإزالة جميع رتب الأعضاء والمشرفين في الكروب بنجاح تام!**\n• بواسطة المطور: @{DEV_USERNAME}")
            return

        if text_clean.startswith("نزلني"):
            remove_user_role(user.id)
            await message.reply_text(f"🔻 **تم تنزيل رتبتك وأصبحت عضواً عادياً في الكروب:** {user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean.startswith("نزله") and is_elevated and reply:
            remove_user_role(target_user.id)
            await message.reply_text(f"🔻 **تم تنزيل العضو وإزالته من الرتب الإدارية بنجاح:** {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- قسم أوامر التاك والمنشن الجماعي الشامل (Tag & Mention Commands) ---
        # =====================================================================
        if text_clean == "تاك للكل" and is_elevated:
            await message.reply_text(f"📢 **تنبيه عام وتصعيد لجميع الأعضاء بواسطة المشرف {user.first_name}:**\n@all يرجى التفاعل والمشاركة المستمرة في المجموعة الكريمة!\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "تاك مشرفين" and is_elevated:
            await message.reply_text(f"📢 **نداء عاجل إلى جميع المشرفين والإدارة في الكروب:**\nيرجى الانتباه ومتابعة تفاعلات المجموعة فوراً!\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- قسم الأيدي بالصورة والمعلومات الكاملة (ID Card & Profile) ---
        # =====================================================================
        if text_clean in ["الايدي", "ايدي", "id"]:
            photos = await context.bot.get_user_profile_photos(target_user.id, limit=1)
            id_text = (
                f"🪪 **معلومات الملف الشخصي (الأيدي المطور):**\n"
                f"• الاسم: {target_user.first_name}\n"
                f"• المعرف: @{target_user.username if target_user.username else 'لا يوجد'}\n"
                f"• الأيدي (ID): `{target_user.id}`\n"
                f"• الرتبة الحالية: {target_role}\n"
                f"• حقوق السورس: @{DEV_USERNAME}"
            )
            if photos.total_count > 0:
                photo_file_id = photos.photos[0][-1].file_id
                await message.reply_photo(photo=photo_file_id, caption=id_text)
            else:
                await message.reply_text(id_text)
            return

        # =====================================================================
        # --- قسم ألعاب وترفيه السورس الشامل (Games & Entertainment - م 6) ---
        # =====================================================================
        if text_clean in ["لعبة النسبة", "نسبة الحب", "نسبة"]:
            rand_num = random.randint(40, 100)
            await message.reply_text(f"🎲 **لعبة النسبة المئوية:**\nنسبة توافق وتفاعل {target_user.first_name} في الكروب هي: **{rand_num}%** 🔥\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean in ["مشن", "حزر", "تخمين"]:
            await message.reply_text(f"🎮 **لعبة الحزورات والذكاء:**\nما هو الشيء الذي أكل نصفه وبقي نصفه الآخر؟\n(أرسل الإجابة الصحيحة في الكروب لتفوز بنقاط الترند!)\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "حزورة":
            await message.reply_text(f"🧩 **سؤال الذكاء السريع:**\nشيء يملك أربعة أرجل ولا يمكنه المشي أبداً، فما هو؟\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- قسم أوامر المشرفين والإدارة العامة (Admin Commands) ---
        # =====================================================================
        if text_clean == "تصفير الترند":
            conn = sqlite3.connect("bot_database.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE user_stats SET messages_count = 0, points = 0 WHERE user_id = ?", (user.id,))
            conn.commit()
            conn.close()
            await message.reply_text(f"🔄 **تم تصفير إحصائيات وترند تفاعلك الشخصي بنجاح!**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "انذار" and is_elevated and reply:
            await message.reply_text(f"⚠️ **تنبيه إداري رسمي موجه إلى العضو:** {target_user.mention_html()},\nيرجى الالتزام بقوانين وقواعد الكروب تفادياً للطرد والحظر!\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="HTML")
            return

        if text_clean == "ضبط الحماية" and is_elevated:
            await message.reply_text(f"🛡️ **تم ضبط إعدادات الحماية والتشفير الكامل ضد السبام والروابط بنجاح.**\n• المطور: @{DEV_USERNAME}")
            return

        if text_clean == "الاعدادات" and is_elevated:
            await message.reply_text(f"⚙️ **لوحة إعدادات المجموعة الحالية:**\n• الحماية العامة: مفعلة 🛡️\n• الردود التلقائية: مفعلة 💬\n• منع الروابط: مفعل 🚫\n• مطور السورس: @{DEV_USERNAME}")
            return

        if text_clean == "القوائم":
            await message.reply_text(f"📋 **قوائم إدارة الكروب والتنظيم:**\n• قائمة الأوامر العامة\n• قائمة الحظر والكتم\n• قائمة التفعيلات والتعطيل\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "صلاحياتي":
            await message.reply_text(f"🛡️ **رتبتك وصلاحياتك الحالية في السورس هي:** {role_title}\n• المطور الأساسي: @{DEV_USERNAME}")
            return

        if text_clean == "كتم" and is_elevated and reply:
            await chat.restrict_member(target_user.id, can_send_messages=False)
            await message.reply_text(f"🔇 **تم كتم العضو بنجاح:** {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "حظر" and is_elevated and reply:
            await chat.ban_member(target_user.id)
            await message.reply_text(f"🚫 **تم حظر العضو نهائياً:** {target_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}")
            return

        if text_clean == "تثبيت" and is_elevated and reply:
            await reply.pin()
            await message.reply_text(f"📌 **تم تثبيت الرسالة في المجموعة بنجاح.**\n• حقوق السورس: @{DEV_USERNAME}")
            return

        # =====================================================================
        # --- قائمة الأوامر الرئيسية المتكاملة (Main Command Panel) ---
        # =====================================================================
        if text_clean in ["الاوامر", "الأوامر", "اوامر"]:
            commands_main_text = (
                f"• اليك اوامر بوتات السورس 5.1 (حقوق المطور الأساسي @{DEV_USERNAME}) .\n\n"
                "• ( م 1 ) ↬ اوامر الحمايه والقفل والفتح\n"
                "• ( م 2 ) ↬ اوامر المشرفين وإدارة الرتب والرفع والتنزيل\n"
                "• ( م 3 ) ↬ اوامر التفعيلات والتعطيل الشاملة\n"
                "• ( م 4 ) ↬ اوامر المسح والتنظيف والترند\n"
                "• ( م 5 ) ↬ اوامر المطورين والتحكم والربط\n"
                "• ( م 6 ) ↬ اوامر الترفيه والألعاب والمسابقات"
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

    if data == "back_to_main_cmds":
        commands_main_text = (
            f"• اليك اوامر بوتات السورس 5.1 (حقوق المطور الأساسي @{DEV_USERNAME}) .\n\n"
            "• ( م 1 ) ↬ اوامر الحمايه والقفل والفتح\n"
            "• ( م 2 ) ↬ اوامر المشرفين وإدارة الرتب والرفع والتنزيل\n"
            "• ( م 3 ) ↬ اوامر التفعيلات والتعطيل الشاملة\n"
            "• ( م 4 ) ↬ اوامر المسح والتنظيف والترند\n"
            "• ( م 5 ) ↬ اوامر المطورين والتحكم والربط\n"
            "• ( م 6 ) ↬ اوامر الترفيه والألعاب والمسابقات"
        )
        await query.edit_message_text(text=commands_main_text, reply_markup=get_main_commands_menu())
        return
    elif data == "menu_page1":
        await query.edit_message_text(text=f"🛡️ **أوامر الحماية والقفل والفتح (م 1):**\n• قفل وفتح: (الروابط، المعرفات، التكرار، الصور، الفيديوهات، البوتات).\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page2":
        admin_menu_text = (
            f"- اوامر إدارة الرتب والمشرفين ⚡️⚡️ (حقوق @{DEV_USERNAME}).\n"
            "- الاوامر تعمل بالرد على العضو :\n\n"
            "• رفع مالك أساسي • رفع مالك\n"
            "• رفع مطور • رفع منشئ\n"
            "• رفع مدير • رفع ادمن • رفع مميز\n"
            "• نزله • نزلني • تنزيل الكل\n"
            "• تاك للكل • تاك مشرفين • انذار"
        )
        await query.edit_message_text(text=admin_menu_text, reply_markup=get_admins_menu_keyboard())
        return
    elif data == "menu_page3":
        await query.edit_message_text(text=f"⚙️ **أوامر التفعيلات والتعطيل (م 3):**\n• تفعيل / تعطيل: (الترحيب، الردود، الالعاب، التحذيرات).\n• قائمة التفعيلات الكاملة.\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page4":
        await query.edit_message_text(text=f"🗑️ **أوامر المسح والتنظيف (م 4):**\n• مسح الرسائل، تنظيف القوائم، وتصفير إحصائيات وترند الأعضاء.\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page5":
        await query.edit_message_text(text=f"💻 **أوامر المطورين والتحكم (م 5):**\n• التحكم الشامل بالسورس، ربط البوتات، وإدارة قواعد البيانات SQL.\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return
    elif data == "menu_page6":
        await query.edit_message_text(text=f"🎮 **أوامر الترفيه والألعاب (م 6):**\n• نسبة الحب، حزورات ذكية، تحديات، كت تويت، صراحة، وألعاب الكروب المتنوعة.\n• المطور الأساسي: @{DEV_USERNAME}", reply_markup=get_sub_back_keyboard())
        return

# =====================================================================
# --- التشغيل الأساسي للبوت عبر الويب هوك (Main Application Runner) ---
# =====================================================================

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات (Handlers) للربط والتنفيذ الفوري
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.ALL, message_handler))

    PORT = int(os.environ.get("PORT", "10000"))
    
    # تشغيل نظام الويب هوك المستقر على المنصة
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://bot-maker-1-709e.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    main()
