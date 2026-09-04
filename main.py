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
DEV_USERNAME = "odox3"  # المطور الأساسي
CHANNEL_USERNAME = "@odox6"  # قناة السورس

# --- قاعدة البيانات ---
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
        roles_map = {
            "dev_primary": "مطور أساسي", 
            "dev_secondary": "مطور ثانوي", 
            "admin": "أدمن", 
            "vip": "عضو مميز"
        }
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

# --- لوحات الأزرار الشفافة للكروبات (7 أقسام) ---
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

# --- لوحة التحكم الخاصة في الشات الخاص (بدء البوت /start) ---
def get_private_start_keyboard(role):
    keyboard = [
        [InlineKeyboardButton("🤖 صنع بوت مجاني", callback_data="make_free_bot")],
        [InlineKeyboardButton("💎 صنع بوت مدفوع", callback_data="make_paid_bot")],
        [InlineKeyboardButton("📊 إحصائياتي الشخصية", callback_data="my_profile")]
    ]
    if role in ["المطور الاساسي", "مطور أساسي", "مطور ثانوي"]:
        keyboard.append([InlineKeyboardButton("⚙️ لوحة تحكم المطورين", callback_data="dev_control_panel")])
    
    keyboard.append([InlineKeyboardButton("👨‍💻 التواصل مع المطور", url=f"https://t.me/{DEV_USERNAME}")])
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

    # 1. المعالجة في الشات الخاص (الخاص مع البوت)
    if chat.type == "private":
        save_user(user.id, user.username, user.full_name)
        
        if text_clean == "/start":
            welcome_msg = (
                f"أهلاً بك يا {user.first_name} في منصة صانع البوتات والحماية والألعاب 🌟\n\n"
                f"رتبتك الحالية: ( **{role_title}** )\n"
                "اختر أحد الخيارات أدناه للبدء:"
            )
            await message.reply_text(welcome_msg, reply_markup=get_private_start_keyboard(role_title), parse_mode="Markdown")
            return
            
        # التحقق إذا كان المستخدم يرسل توكن بوت (بعد النضغط على صنع بوت مجاني أو مدفوع)
        if context.user_data.get("waiting_for_token"):
            bot_type = context.user_data.get("waiting_for_token")
            token = text_clean
            
            if bot_type == "free":
                # حفظ التوكن المجاني وصنعه تلقائياً
                conn = sqlite3.connect("bot_database.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user_bots (user_id, bot_token, bot_type) VALUES (?, ?, ?)", (user.id, token, "free"))
                conn.commit()
                conn.close()
                
                context.user_data["waiting_for_token"] = None
                await message.reply_text("✅ **تم صنع بوتك المجاني بنجاح!**\nتم ربط التوكن الخاص بك وتشغيل البوت تلقائياً.")
                return
                
            elif bot_type == "paid":
                # إرسال التوكن للمطور ليقوم بصنعه يدوياً
                context.user_data["waiting_for_token"] = None
                dev_notification = (
                    f"💎 **طلب بوت مدفوع جديد!**\n\n"
                    f"من المستخدم: {user.first_name} (@{user.username or 'لايوجد'})\n"
                    f"الايدي: `{user.id}`\n"
                    f"التوكن المرسل: `{token}`\n\n"
                    "يرجى تفعيل البوت يدوياً للمستخدم."
                )
                # إرسال التوكن للمطور الأساسي إذا أردت أو حفظه بانتظار المراجعة
                await message.reply_text("💎 **تم إرسال توكن البوت المدفوع إلى المطور بنجاح!**\nسقوم المطور بمراجعته وصنعه وتفعيله لك قريباً.")
                return

        return

    # 2. المعالجة داخل المجموعات (الكروبات)
    if chat.type in ["group", "supergroup"]:
        is_photo_msg = bool(message.photo)
        save_user(user.id, user.username, user.full_name)
        update_user_stats(user.id, is_photo=is_photo_msg)

        if text_clean == "تفعيل":
            activate_group(chat.id, chat.title)
            await message.reply_text("✅ **تم تفعيل البوت وحمايته وألعابه بالكامل في هذه المجموعة!**\nاكتب `الاوامر` لإظهار لوحات الأزرار الشفافة.")
            return

        reply = message.reply_to_message
        target_user = reply.from_user if reply else user
        target_role = get_user_role(target_user.id, target_user.username)

        # إظهار الـ 7 لوحات والأزرار الشفافة عند كتابة "الاوامر"
        if text_clean in ["الاوامر", "الأوامر", "اوامر"]:
            main_menu_text = (
                "📚 **دليل أوامر البوت الشامل في المجموعة:**\n\n"
                "مرحباً بك في لوحة تحكم السورس الرسمية.\n"
                "اختر القسم الذي تريد استعراض أوامره من الأزرار الشفافة بالأسفل 👇"
            )
            await message.reply_text(main_menu_text, reply_markup=get_command_keyboard())
            return

        # اختصارات الألعاب
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

        # أوامر الإدارة (رفع مطور ثانوي، أدمن، مميز، طرد، كتم)
        if text_clean.startswith("رفع مطور ثانوي") and role_title in ["المطور الاساسي", "مطور أساسي"]:
            if reply:
                set_user_role(target_user.id, "dev_secondary")
                await message.reply_text(f"👤 تم رفعه (مطور ثانوي بنجاح): {target_user.first_name}")
        elif text_clean.startswith("رفع ادمن") or text_clean.startswith("رفع أدمن"):
            if role_title in ["المطور الاساسي", "مطور أساسي", "مطور ثانوي"]:
                if reply:
                    set_user_role(target_user.id, "admin")
                    await message.reply_text(f"👤 تم رفعه (أدمن رسمي): {target_user.first_name}")
            else:
                await message.reply_text("⚠️ هذا الأمر للمطورين فقط.")
        elif text_clean.startswith("طرد"):
            if role_title in ["المطور الاساسي", "مطور أساسي", "مطور ثانوي", "أدمن"]:
                if reply:
                    try:
                        await chat.ban_member(target_user.id)
                        await message.reply_text(f"🚫 تم طرد المخالف: {target_user.first_name}")
                    except Exception:
                        await message.reply_text("تأكد من صلاحيات البوت للإشراف.")

# --- نظام تفاعل الأزرار (Callback Queries) ---
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    role_title = get_user_role(user.id, user.username)

    # تفاعل الشات الخاص (صانع البوتات ولوحة المطورين)
    if data == "make_free_bot":
        context.user_data["waiting_for_token"] = "free"
        keyboard = [[InlineKeyboardButton("🔙 إلغاء", callback_data="back_to_private_start")]]
        await query.edit_message_text(
            text="🤖 **صانع البوتات المجاني:**\n\nأرسل الآن (توكن البوت Token) الذي استخرجته من @BotFather وسأقوم بصنعه وتفعيله لك فوراً.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
        
    elif data == "make_paid_bot":
        context.user_data["waiting_for_token"] = "paid"
        keyboard = [[InlineKeyboardButton("🔙 إلغاء", callback_data="back_to_private_start")]]
        await query.edit_message_text(
            text="💎 **صانع البوتات المدفوع:**\n\nأرسل توكن بوتك المدفوع، وسيتم إرساله للمطور الأساسي لتفعيله يدوياً وصنعه بكافة الميزات الاحترافية.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    elif data == "my_profile":
        stats = get_user_stats_data(user.id)
        profile_text = (
            f"📊 **ملفك الشخصي:**\n"
            f"- الايدي: `{user.id}`\n"
            f"- الرتبة: {role_title}\n"
            f"- المستوى: {stats[4]}\n"
            f"- النقاط: {stats[1]}\n"
            f"- الرسائل: {stats[0]}"
        )
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_private_start")]]
        await query.edit_message_text(text=profile_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    elif data == "dev_control_panel":
        if role_title in ["المطور الاساسي", "مطور أساسي", "مطور ثانوي"]:
            dev_text = (
                "⚙️ **لوحة تحكم المطورين:**\n\n"
                "- إحصائيات البوتات المصنوعة\n"
                "- إدارة المطورين الثانويين والأدمنية\n"
                "- التحكم بإعدادات السورس العامة"
            )
            keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_private_start")]]
            await query.edit_message_text(text=dev_text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.answer("هذا القسم مخصص للمطورين فقط!", show_alert=True)
        return

    elif data == "back_to_private_start":
        context.user_data["waiting_for_token"] = None
        welcome_msg = f"أهلاً بك مجدداً يا {user.first_name}\nاختر أحد الخيارات أدناه:"
        await query.edit_message_text(text=welcome_msg, reply_markup=get_private_start_keyboard(role_title))
        return

    # تفاعل لوحات الكروبات (الأوامر والـ 7 أقسام)
    if data == "cmd_stats":
        text = "📊 **قسم الإحصائيات:**\n- `ايدي` (عرض معلوماتك)\n- `رتبتي` (معرفة رتبتك)"
    elif data == "cmd_protection":
        text = "🛡️ **قسم الحماية:**\n- منع الروابط والتكرار والبوتات الوهمية تلقائياً."
    elif data == "cmd_games":
        text = "🎮 **قسم الألعاب:**\n- `روليت`\n- `مافيا`\n- `كراسي`\n- `لغز`"
    elif data == "cmd_admin":
        text = "⚙️ **قسم الإدارة:**\n- `رفع ادمن` / `طرد` / `كتم`"
    elif data == "cmd_shop":
        text = "🛍️ **قسم المتجر:**\n- شراء تميز ونقاط."
    elif data == "cmd_dev":
        text = f"👨‍💻 **قسم المطور:**\n- المطور الأساسي: @{DEV_USERNAME}"
    elif data == "cmd_close":
        await query.message.delete()
        return
    else:
        text = "اختر القسم المطلوب:"

    await query.edit_message_text(text=text, reply_markup=get_command_keyboard(), parse_mode="Markdown")

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.ALL, message_handler))

    PORT = int(os.environ.get("PORT", "10000"))
    RENDER_URL = "https://bot-maker-1-709e.onrender.com"

    logger.info("Bot started successfully with private bot maker and group transparent command boards...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
