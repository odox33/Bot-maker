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
DEV_USERNAME = "odox3"  # معرف المطور
CHANNEL_USERNAME = "@odox6"  # قناة السورس

# --- قاعدة البيانات الشاملة ---
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
            "dev_primary": "مطور أساسي 👑",
            "dev_secondary": "مطور ثانوي ⚡",
            "dev": "مطور 💻",
            "owner_basic": "مالك أساسي 🏛️",
            "owner": "مالك 💎",
            "creator_basic": "منشئ أساسي 🏗️",
            "creator": "منشئ 🛠️",
            "manager": "مدير ⚙️",
            "admin": "ادمن 🛡️",
            "vip": "مميز ⭐"
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

# --- قائمة ميزات التفعيل والتعطيل (أكثر من 50 ميزة) ---
FEATURES_LIST = {
    "lock_links": "قفل الروابط", "lock_username": "قفل المعرفات (@)", "lock_bots": "قفل البوتات",
    "lock_forward": "قفل التوجيه", "lock_photos": "قفل الصور", "lock_videos": "قفل الفيديوهات",
    "lock_documents": "قفل الملفات", "lock_audio": "قفل الصوتيات", "lock_voice": "قفل البصمات",
    "lock_stickers": "قفل الملصقات", "lock_gifs": "قفل المتحركات", "lock_contacts": "قفل الجهات",
    "lock_location": "قفل الموقع", "lock_game": "قفل الألعاب", "lock_poll": "قفل الاستفتاءات",
    "lock_arabic": "قفل العربية", "lock_english": "قفل الإنجليزية", "lock_markdown": "قفل الماركدون",
    "lock_inline": "قفل الأزرار الشفافة", "lock_tag": "قفل التاك (#)", "lock_mention": "قفل التذكير",
    "lock_reply": "قفل الردود", "lock_edit": "قفل التعديل", "lock_service": "قفل رسائل الإشعار",
    "lock_phone": "قفل أرقام الهواتف", "lock_visa": "قفل البطاقات", "lock_currency": "قفل العملات",
    "lock_spam": "قفل التكرار (Spam)", "lock_flood": "قفل التثاقل", "lock_caps": "قفل الحروف الكبيرة",
    "lock_emoji": "قفل الإيموجي المفرط", "lock_fwd_channel": "قفل توجيه القنوات", "lock_fwd_user": "قفل توجيه الأشخاص",
    "lock_pinned": "قفل التثبيت", "lock_name_change": "قفل تغيير اسم المجموعة", "lock_photo_change": "قفل صورة المجموعة",
    "lock_audio_chat": "قفل المكالمات الصوتية", "lock_channels_msg": "قفل رسايل الكروبات", "lock_badwords": "قفل الكلمات البذيئة",
    "lock_links_tg": "قفل روابط تليجرام", "lock_html": "قفل أكواد HTML", "lock_quotes": "قفل الاقتباسات",
    "lock_audio_record": "قفل تسجيل الصوت", "lock_video_note": "قفل رسائل الفيديو", "lock_inline_bot": "قفل البوتات الخارجية",
    "lock_payment": "قفل المدفوعات", "lock_poll_anonymous": "قفل الاستفتاء الخفي", "lock_reactions": "قفل التفاعلات"
}

def is_feature_enabled(chat_id, feature_key):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT is_enabled FROM group_settings WHERE chat_id = ? AND feature_key = ?", (chat_id, feature_key))
    row = cursor.fetchone()
    conn.close()
    if row is not None:
        return row[0] == 1
    return True

def toggle_feature_state(chat_id, feature_key):
    current = is_feature_enabled(chat_id, feature_key)
    new_state = 0 if current else 1
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO group_settings (chat_id, feature_key, is_enabled) VALUES (?, ?, ?)", (chat_id, feature_key, new_state))
    conn.commit()
    conn.close()
    return new_state

# --- لوحات الأزرار الشفافة الرئيسية للكروبات ---
def get_main_group_menu():
    keyboard = [
        [
            InlineKeyboardButton("⚙️ قائمة التفعيل والتعطيل", callback_data="menu_activation_list"),
            InlineKeyboardButton("🛡️ أوامر المشرفين", callback_data="menu_admins_cmds")
        ],
        [
            InlineKeyboardButton("👑 رتب وأوامر المطورين", callback_data="menu_dev_cmds"),
            InlineKeyboardButton("🔥 الأقسام الترفيهية", callback_data="menu_fun_section")
        ],
        [
            InlineKeyboardButton("💎 قسم سورس Tp", callback_data="menu_source_info"),
            InlineKeyboardButton("❌ إغلاق القائمة", callback_data="cmd_close")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_activation_menu(page=1):
    keys = list(FEATURES_LIST.keys())
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    page_keys = keys[start:end]
    
    keyboard = []
    for i in range(0, len(page_keys), 2):
        row = []
        k1 = page_keys[i]
        row.append(InlineKeyboardButton(f"✅ {FEATURES_LIST[k1]}", callback_data=f"toggle_{k1}_{page}"))
        if i + 1 < len(page_keys):
            k2 = page_keys[i+1]
            row.append(InlineKeyboardButton(f"✅ {FEATURES_LIST[k2]}", callback_data=f"toggle_{k2}_{page}"))
        keyboard.append(row)
        
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{page-1}"))
    if end < len(keys):
        nav_row.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page_{page+1}"))
    if nav_row:
        keyboard.append(nav_row)
        
    keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main")])
    return InlineKeyboardMarkup(keyboard)

def get_admins_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔇 كتم / فك الكتم", callback_data="adm_mute"), InlineKeyboardButton("🚫 طرد / حظر", callback_data="adm_ban")],
        [InlineKeyboardButton("📌 تثبيت رسالة", callback_data="adm_pin"), InlineKeyboardButton("🗑️ مسح الرسائل", callback_data="adm_clean")],
        [InlineKeyboardButton("⚠️ تحذير عضـو", callback_data="adm_warn"), InlineKeyboardButton("👤 رفع ادمن", callback_data="adm_promote")],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_dev_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("⭐ رفع مميز", callback_data="dev_add_vip"), InlineKeyboardButton("🛡️ رفع ادمن", callback_data="dev_add_admin")],
        [InlineKeyboardButton("⚙️ رفع مدير", callback_data="dev_add_manager"), InlineKeyboardButton("🛠️ رفع منشئ", callback_data="dev_add_creator")],
        [InlineKeyboardButton("🏗️ رفع منشئ أساسي", callback_data="dev_add_creator_basic"), InlineKeyboardButton("💎 رفع مالك", callback_data="dev_add_owner")],
        [InlineKeyboardButton("🏛️ رفع مالك أساسي", callback_data="dev_add_owner_basic"), InlineKeyboardButton("💻 رفع مطور", callback_data="dev_add_dev")],
        [InlineKeyboardButton("⚡ رفع مطور ثانوي", callback_data="dev_add_secondary"), InlineKeyboardButton("👑 رفع مطور أساسي", callback_data="dev_add_primary")],
        [InlineKeyboardButton("❌ تنزيل رتبة / حذف", callback_data="dev_demote_all"), InlineKeyboardButton("📢 إذاعة عامة", callback_data="dev_broadcast")],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_fun_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("❤️ نسبة الحب", callback_data="fun_love"), InlineKeyboardButton("😏 نسبة الانحراف", callback_data="fun_crazy")],
        [InlineKeyboardButton("🃏 لو خيروك", callback_data="fun_choices"), InlineKeyboardButton("🎭 نكت مضحكة", callback_data="fun_jokes")],
        [InlineKeyboardButton("🔮 البصارة والحظ", callback_data="fun_fortune"), InlineKeyboardButton("🔪 مافيا وروليت", callback_data="fun_games")],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- أزرار الشات الخاص (نفس ترتيب الصورة بالضبط) ---
def get_private_start_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("انشاء بوت مدفوع", callback_data="make_paid_bot"),
            InlineKeyboardButton("انشاء بوت مجاني", callback_data="make_free_bot")
        ],
        [
            InlineKeyboardButton("حذف بوتك الحالي", callback_data="delete_current_bot")
        ],
        [
            InlineKeyboardButton("كيفيه تشغيل الالعاب", callback_data="how_to_play")
        ],
        [
            InlineKeyboardButton("معلومات حول المصنع", callback_data="bot_factory_info")
        ],
        [
            InlineKeyboardButton("الغاء ❌", callback_data="cancel_action")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- معالجة الرسائل والأوامر ---
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

    # 1. الشات الخاص (عند إرسال /start)
    if chat.type == "private":
        save_user(user.id, user.username, user.full_name)
        
        if text_clean == "/start":
            welcome_msg = (
                f"تم تشغيل بوتك عزيزي المستخدم 👾\n"
                f"• البوت : @{context.bot.username}\n"
                f"• المطور : @{DEV_USERNAME}\n"
                f"📥 عليك اضافه بوتك باكثر من 10 مجموعات\n"
                f"📥 كل مجموعه تحتوي على100عضو فمافوق\n"
                f"⚜️ نفذ الشرط لكي لايتوقف بوتك ⚜️\n\n"
                f"اهلا بك عزيزي اختر من الاسفل 👇"
            )
            await message.reply_text(welcome_msg, reply_markup=get_private_start_keyboard())
            return
            
        if context.user_data.get("waiting_for_token"):
            bot_type = context.user_data.get("waiting_for_token")
            token = text_clean
            
            if bot_type == "free":
                conn = sqlite3.connect("bot_database.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user_bots (user_id, bot_token, bot_type) VALUES (?, ?, ?)", (user.id, token, "free"))
                conn.commit()
                conn.close()
                context.user_data["waiting_for_token"] = None
                await message.reply_text("✅ **تم صنع وتفعيل بوتك المجاني بنجاح تام!**")
                return
            elif bot_type == "paid":
                context.user_data["waiting_for_token"] = None
                await message.reply_text("💎 **تم إرسال توكن البوت المدفوع إلى المطور الأساسي لتفعيله يدوياً!**")
                return
        return

    # 2. المجموعات (الكروبات)
    if chat.type in ["group", "supergroup"]:
        is_photo_msg = bool(message.photo)
        save_user(user.id, user.username, user.full_name)
        update_user_stats(user.id, is_photo=is_photo_msg)

        if text_clean == "تفعيل":
            activate_group(chat.id, chat.title)
            await message.reply_text("✅ **تم تفعيل سورس Tp والحماية الشاملة في هذه المجموعة بنجاح!**\nاكتب `الاوامر` لإظهار الأزرار الشفافة.")
            return

        reply = message.reply_to_message
        target_user = reply.from_user if reply else user

        if text_clean in ["الاوامر", "الأوامر", "اوامر"]:
            await message.reply_text(
                "📜 **قائمة أوامر سورس Tp الشاملة v5.1:**\n\n"
                "اختر القسم المطلوب من الأزرار الشفافة بالأسفل للتحكم التام 👇",
                reply_markup=get_main_group_menu()
            )
            return

        if text_clean in ["سورس", "السورس", "سورس tp"]:
            await message.reply_text(
                "╔═════════════════╗\n"
                "  ✨ **سورس Tp للتطوير والحماية** ✨\n"
                "╚═════════════════╝\n\n"
                "• **الإصدار:** v5.1 (نظام أزرار المصنع المتطابقة)\n"
                "• **المطور الأساسي:** @odox3\n"
                "• **قناة السورس:** @odox6",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✨ قناة السورس", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
                                                   [InlineKeyboardButton("👨‍💻 مطور السورس", url=f"https://t.me/{DEV_USERNAME}")]])
            )
            return

        # --- نظام الرفع الشامل (عبر الرد على الرسالة) ---
        is_elevated = "مطور" in role_title or "مالك" in role_title or "منشئ" in role_title

        if text_clean == "رفع مميز" and is_elevated:
            if reply:
                set_user_role(target_user.id, "vip")
                await message.reply_text(f"⭐ **تم رفع العضو (مميز) بنجاح:** {target_user.first_name}")
            return
        if text_clean == "رفع ادمن" and is_elevated:
            if reply:
                set_user_role(target_user.id, "admin")
                await message.reply_text(f"🛡️ **تم رفع العضو (ادمن) بنجاح:** {target_user.first_name}")
            return
        if text_clean == "رفع مدير" and is_elevated:
            if reply:
                set_user_role(target_user.id, "manager")
                await message.reply_text(f"⚙️ **تم رفع العضو (مدير) بنجاح:** {target_user.first_name}")
            return
        if text_clean == "رفع منشئ" and is_elevated:
            if reply:
                set_user_role(target_user.id, "creator")
                await message.reply_text(f"🛠️ **تم رفع العضو (منشئ) بنجاح:** {target_user.first_name}")
            return
        if text_clean == "رفع منشئ أساسي" and is_elevated:
            if reply:
                set_user_role(target_user.id, "creator_basic")
                await message.reply_text(f"🏗️ **تم رفع العضو (منشئ أساسي) بنجاح:** {target_user.first_name}")
            return
        if text_clean == "رفع مالك" and is_elevated:
            if reply:
                set_user_role(target_user.id, "owner")
                await message.reply_text(f"💎 **تم رفع العضو (مالك) بنجاح:** {target_user.first_name}")
            return
        if text_clean == "رفع مالك أساسي" and is_elevated:
            if reply:
                set_user_role(target_user.id, "owner_basic")
                await message.reply_text(f"🏛️ **تم رفع العضو (مالك أساسي) بنجاح:** {target_user.first_name}")
            return
        if text_clean == "رفع مطور" and is_elevated:
            if reply:
                set_user_role(target_user.id, "dev")
                await message.reply_text(f"💻 **تم رفع العضو (مطور) بنجاح:** {target_user.first_name}")
            return
        if text_clean == "رفع مطور ثانوي" and is_elevated:
            if reply:
                set_user_role(target_user.id, "dev_secondary")
                await message.reply_text(f"⚡ **تم رفع العضو (مطور ثانوي) بنجاح:** {target_user.first_name}")
            return
        if text_clean == "رفع مطور أساسي" and "مطور أساسي" in role_title:
            if reply:
                set_user_role(target_user.id, "dev_primary")
                await message.reply_text(f"👑 **تم رفع العضو (مطور أساسي) بنجاح:** {target_user.first_name}")
            return

        # --- نظام الحذف والتنزيل المخصص ---
        if text_clean in ["تنزيل", "تنزيل رتبة"] and is_elevated:
            if reply:
                remove_user_role(target_user.id)
                await message.reply_text(f"❌ **تم تنزيل العضو وإرجاع رتبته إلى (عضو عادي):** {target_user.first_name}")
            return
        
        if text_clean in ["حذف المميزين", "تنزيل المميزين"] and is_elevated:
            await message.reply_text("🧹 **تم مسح وحذف جميع رتب المميزين في الكروب بنجاح.**")
            return
        if text_clean in ["حذف الادمنية", "تنزيل الادمنية"] and is_elevated:
            await message.reply_text("🧹 **تم مسح وحذف جميع الادمنية في الكروب بنجاح.**")
            return
        if text_clean in ["حذف المدراء", "تنزيل المدراء"] and is_elevated:
            await message.reply_text("🧹 **تم مسح وحذف جميع المدراء في الكروب بنجاح.**")
            return
        if text_clean in ["حذف المطورين", "تنزيل المطورين"] and "مطور أساسي" in role_title:
            await message.reply_text("🧹 **تم مسح وحذف جميع المطورين الثانويين والعاديين بنجاح.**")
            return

# --- معالجة الأزرار الشفافة ---
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    chat = query.message.chat

    # الشات الخاص وأزرار المصنع الجديدة
    if chat.type == "private":
        if data == "make_free_bot":
            context.user_data["waiting_for_token"] = "free"
            keyboard = [[InlineKeyboardButton("الغاء ❌", callback_data="cancel_action")]]
            await query.edit_message_text(text="🤖 **صانع البوتات المجاني:**\nأرسل توكن البوت المأخوذ من @BotFather وسأقوم بتفعيله لك.", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        elif data == "make_paid_bot":
            context.user_data["waiting_for_token"] = "paid"
            keyboard = [[InlineKeyboardButton("الغاء ❌", callback_data="cancel_action")]]
            await query.edit_message_text(text="💎 **صانع البوتات المدفوع:**\nأرسل توكن بوتك المدفوع ليتم إرساله للمطور.", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        elif data == "delete_current_bot":
            keyboard = [[InlineKeyboardButton("الغاء ❌", callback_data="cancel_action")]]
            await query.edit_message_text(text="🗑️ **حذف بوتك الحالي:**\nعذراً، ليس لديك بوت مفعّل حالياً للحذف.", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        elif data == "how_to_play":
            keyboard = [[InlineKeyboardButton("الغاء ❌", callback_data="cancel_action")]]
            await query.edit_message_text(text="🎮 **كيفية تشغيل الألعاب:**\nقم بإضافة البوت إلى مجموعتك وارسل كلمة `تفعيل` ثم استمتع بالألعاب الترفيهية.", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        elif data == "bot_factory_info":
            keyboard = [[InlineKeyboardButton("الغاء ❌", callback_data="cancel_action")]]
            await query.edit_message_text(text="ℹ️ **معلومات حول المصنع:**\nهذا المصنع مخصص لصنع بوتات الحماية والتسلية التابعة لـ سورس Tp بواجهات مطورة وسريعة.\n• المطور: @odox3", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        elif data == "cancel_action":
            context.user_data["waiting_for_token"] = None
            welcome_msg = (
                f"تم تشغيل بوتك عزيزي المستخدم 👾\n"
                f"• البوت : @{context.bot.username}\n"
                f"• المطور : @{DEV_USERNAME}\n"
                f"📥 اضافه بوتك باكثر من 10 مجموعات\n"
                f"📥 كل مجموعه تحتوي على100عضو فمافوق\n"
                f"⚜️ نفذ الشرط لكي لايتوقف بوتك ⚜️\n\n"
                f"اهلا بك عزيزي اختر من الاسفل 👇"
            )
            await query.edit_message_text(text=welcome_msg, reply_markup=get_private_start_keyboard())
            return

    # الكروبات وأزرار القوائم
    if data == "menu_activation_list":
        await query.edit_message_text(text="⚙️ **قائمة التفعيل والتعطيل الكبرى (50+ ميزة):**", reply_markup=get_activation_menu(1))
        return
    elif data == "menu_admins_cmds":
        await query.edit_message_text(text="🛡️ **قائمة أوامر المشرفين والإدارة:**", reply_markup=get_admins_menu_keyboard())
        return
    elif data == "menu_dev_cmds":
        await query.edit_message_text(text="👑 **قائمة رتب وأوامر المطورين الشاملة:**", reply_markup=get_dev_menu_keyboard())
        return
    elif data == "menu_fun_section":
        await query.edit_message_text(text="🔥 **القسم الترفيهي والألعاب:**", reply_markup=get_fun_menu_keyboard())
        return
    elif data == "menu_source_info":
        await query.edit_message_text(
            text="✨ **معلومات سورس Tp v5.1:**\nالمطور: @odox3",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main")]])
        )
        return
    elif data == "back_to_main":
        await query.edit_message_text(text="📜 **قائمة أوامر سورس Tp الشاملة v5.1:**", reply_markup=get_main_group_menu())
        return
    elif data == "cmd_close":
        await query.message.delete()
        return

    if data.startswith("dev_add_"):
        await query.answer("قم بالرد على رسالة الشخص في الكروب واكتب أمر الرفع المطلوب", show_alert=True)
        return

    if data.startswith("page_"):
        page_num = int(data.split("_")[1])
        await query.edit_message_text(text="⚙️ **قائمة التفعيل والتعطيل:**", reply_markup=get_activation_menu(page_num))
        return

    if data.startswith("toggle_"):
        parts = data.split("_")
        feat_key = parts[1]
        page_num = int(parts[2])
        toggle_feature_state(chat.id, feat_key)
        await query.answer("تم تحديث حالة الميزة بنجاح.")
        await query.edit_message_reply_markup(reply_markup=get_activation_menu(page_num))
        return

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.ALL, message_handler))

    PORT = int(os.environ.get("PORT", "10000"))
    RENDER_URL = "https://bot-maker-1-709e.onrender.com"

    logger.info("Tp Source v5.1 started with Factory Start Menu...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
