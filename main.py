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

# --- قاعدة البيانات المركزية الشاملة ---
def init_db():
    conn = sqlite3.connect("bot_database.db", timeout=30.0)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('forced_sub', 'active')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('paid_bots_active', 'active')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('free_bots_active', 'active')")
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
    # جدول ألعاب المجموعات والتحكم
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_settings (
            chat_id INTEGER PRIMARY KEY,
            lock_links TEXT DEFAULT 'open',
            lock_flood TEXT DEFAULT 'open',
            lock_bots TEXT DEFAULT 'open',
            welcome_msg TEXT DEFAULT 'مرحباً بك في المجموعة'
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
        logger.error(f"DB Error save_user: {e}")

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
        logger.error(f"DB Error update_stats: {e}")

def get_user_stats_data(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT messages_count, points, photos_count, typos_count, level FROM user_stats WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (0, 0, 0, 0, 'مبتدئ')

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
    cursor.execute("INSERT OR IGNORE INTO group_settings (chat_id) VALUES (?)", (chat_id,))
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

# --- الواجهة الرئيسية للبوت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    save_user(user.id, user.username, user.full_name)
    role_title = get_user_role(user.id, user.username)
    
    if chat.type in ["group", "supergroup"]:
        await update.message.reply_text("أهلاً بك في Hexon Games 🌟\nالبوت جاهز لإدارة الحماية والألعاب الضخمة.\nاكتب **تفعيل** لتفعيل البوت رسمياً هنا.")
        return

    if role_title == "المطور الاساسي":
        keyboard = [
            [InlineKeyboardButton("⚙️ إعدادات البوت والتحكم الأساسي", callback_data="admin_settings")],
            [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
            [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
            [InlineKeyboardButton("📊 إحصائياتي الشاملة", callback_data="get_my_id")],
            [InlineKeyboardButton("🎮 قسم الألعاب والتسلية", callback_data="games_menu")],
            [InlineKeyboardButton("🛍️ المتجر والترقيات", callback_data="shop_menu")],
            [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")]
        ]
        welcome_text = f"أهلاً بك يا مطورنا الأساسي في لوحة تحكم المنصة الشاملة:"
    else:
        keyboard = [
            [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
            [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
            [InlineKeyboardButton("📊 إحصائياتي الشاملة", callback_data="get_my_id")],
            [InlineKeyboardButton("🎮 قسم الألعاب والتسلية", callback_data="games_menu")],
            [InlineKeyboardButton("🛍️ المتجر والترقيات", callback_data="shop_menu")],
            [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")]
        ]
        welcome_text = f"أهلاً بك يا {user.first_name} في منصة الألعاب والحماية المتكاملة."

    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text=welcome_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=welcome_text, reply_markup=reply_markup)

# --- معالجة الأزرار التفاعلية ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    role_title = get_user_role(user.id, user.username)
    await query.answer()
    
    if query.data == "free_bot_maker":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(text="🛠 **قسم صانع البوتات المجاني:**\n\nأرسل توكن بوتك الجديد للبدء بصنعه فوراً.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif query.data == "paid_bot_maker":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(text="💎 **قسم صانع البوتات المدفوع:**\n\nبوتات احترافية للألعاب والحماية بدون رعاية!", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif query.data == "games_menu":
        keyboard = [
            [InlineKeyboardButton("🎲 روليت", callback_data="game_roulette"), InlineKeyboardButton("🕵️‍♂️ مافيا", callback_data="game_mafia")],
            [InlineKeyboardButton("🪑 لعبة الكراسي", callback_data="game_chairs"), InlineKeyboardButton("🙈 غميضة", callback_data="game_hide")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
        ]
        await query.edit_message_text(text="🎮 **قائمة الألعاب المتاحة:**\nاختر اللعبة التي تريد معرفة تفاصيلها أو بدئها في المجموعات:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif query.data in ["game_roulette", "game_mafia", "game_chairs", "game_hide"]:
        game_names = {"game_roulette": "روليت الحظ", "game_mafia": "المافيا الخطيرة", "game_chairs": "لعبة الكراسي الموسيقية", "game_hide": "الغميضة"}
        g_name = game_names.get(query.data, "لعبة عامة")
        keyboard = [[InlineKeyboardButton("🔙 رجوع للألعاب", callback_data="games_menu")]]
        await query.edit_message_text(text=f"🎮 **{g_name}:**\nلعب هذه اللعبة يتطلب تواجُدك في مجموعة مفعلة.\nفقط اكتب اسم اللعبة في مجموعتك المفعلة للبدء فوراً!", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "shop_menu":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(text="🛍️ **متجر المنصة:**\n- شراء نقاط إضافية (متاحة)\n- ترقية الرتب داخل المجموعات\nتواصل مع المطور لشراء الخدمات الخاصة.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
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
            f"- : مستواك : ( {stats[4]} )\n"
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
                [InlineKeyboardButton("📊 إحصائياتي الشاملة", callback_data="get_my_id")],
                [InlineKeyboardButton("🎮 قسم الألعاب والتسلية", callback_data="games_menu")],
                [InlineKeyboardButton("🛍️ المتجر والترقيات", callback_data="shop_menu")],
                [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
                [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
                [InlineKeyboardButton("📊 إحصائياتي الشاملة", callback_data="get_my_id")],
                [InlineKeyboardButton("🎮 قسم الألعاب والتسلية", callback_data="games_menu")],
                [InlineKeyboardButton("🛍️ المتجر والترقيات", callback_data="shop_menu")],
                [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")]
            ]
        await query.edit_message_text(text="القائمة الرئيسية:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- معالجة الأوامر والميزات الشاملة داخل المجموعات ---
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

    # تتبع الأنشطة والإحصائيات في الكروبات
    if chat.type in ["group", "supergroup"]:
        is_photo_msg = bool(message.photo)
        save_user(user.id, user.username, user.full_name)
        update_user_stats(user.id, is_photo=is_photo_msg)

    # 1. أمر التفعيل
    if text_clean == "تفعيل":
        if chat.type in ["group", "supergroup"]:
            activate_group(chat.id, chat.title)
            await message.reply_text("✅ تم تفعيل البوت وحمايته وألعابه في هذه المجموعة بنجاح!")
            return

    if chat.type not in ["group", "supergroup"]:
        return

    role_title = get_user_role(user.id, user.username)
    reply = message.reply_to_message

    # تحديد الهدف الذكي (بالرد أو بالاسم)
    target_user = reply.from_user if reply else user
    target_role = get_user_role(target_user.id, target_user.username)

    # 2. أمر الآيدي الشامل
    if text_clean in ["ايدي", "/id", "ID", "الايدي"]:
        photos = await context.bot.get_user_profile_photos(target_user.id, limit=1)
        stats = get_user_stats_data(target_user.id)
        username_str = f"@{target_user.username}" if target_user.username else "لا يوجد"
        
        text_id = (
            f"- : ايديك : ( {target_user.id} )\n"
            f"- : معرفك : ( {username_str} )\n"
            f"- : رتبتك : ( {target_role} )\n"
            f"- : مستواك : ( {stats[4]} )\n"
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

    # 3. أمر الرتبة
    if text_clean in ["رتبتي", "الرتبة"]:
        await message.reply_text(f"- : رتبتك هي : ( {target_role} )")
        return

    # 4. نظام الألعاب المتطورة داخل المجموعات
    if text_clean in ["روليت", "لعبة روليت"]:
        lucky_points = random.randint(10, 100)
        await message.reply_text(f"🎲 **لعبة روليت الحظ:**\nأدار {user.first_name} عجلة الحظ وفاز بـ **{lucky_points}** نقطة إضافية!")
        return
    elif text_clean in ["مافيا", "لعبة مافيا"]:
        await message.reply_text("🕵️‍♂️ **لعبة المافيا:**\nبدأت لعبة التصويت! من هو المشتبه به بينكم؟ شاركوا بآرائكم.")
        return
    elif text_clean in ["لعبة الكراسي", "كراسي"]:
        await message.reply_text("🪑 **لعبة الكراسي الموسيقية:**\nتوقف الموسيقا! أسرع واكتب `جلس` لتحجز مقعدك الفائز!")
        return
    elif text_clean in ["غميضة", "لعبة غميضة"]:
        await message.reply_text("🙈 **لعبة الغميضة:**\nتم إخفاء المتسابقين، ابدأوا بالبحث واستخدام تلميحات البوت.")
        return
    elif text_clean == "جلس":
        await message.reply_text(f"🪑 الكابتن **{user.first_name}** جلس على الكرسي وأخذ مقعده بنجاح!")
        return

    # 5. الإحصائيات والمتجر
    elif text_clean in ["الاحصائيات", "إحصائياتي"]:
        stats = get_user_stats_data(target_user.id)
        await message.reply_text(f"📊 **إحصائيات المستخدم {target_user.first_name}:**\n💬 الرسائل: {stats[0]}\n⭐ النقاط: {stats[1]}\n📸 الصور: {stats[2]}\n🏆 المستوى: {stats[4]}")
        return
    elif text_clean in ["المتجر", "shop"]:
        await message.reply_text("🛍️ **متجر المجموعة:**\n1. شراء تميز لمدة أسبوع (50 نقطة)\n2. تصفية السحكات (30 نقطة)\nتواصل مع إدارة البوت لتفعيل مشترياتك.")
        return

    # 6. أوامر الإدارة الشاملة (رفع أدمن، مطور، مميز، طرد، كتم، إلخ)
    if text_clean.startswith("رفع مطور أساسي") and role_title == "المطور الاساسي":
        if reply:
            set_user_role(target_user.id, "dev")
            await message.reply_text(f"👤 تم رفعه (مطور أساسي بنجاح): {target_user.first_name}")
    elif text_clean.startswith("رفع ادمن") or text_clean.startswith("رفع أدمن"):
        if role_title in ["المطور الاساسي", "مطور أساسي"]:
            if reply:
                set_user_role(target_user.id, "admin")
                await message.reply_text(f"👤 تم رفعه (أدمن بنجاح): {target_user.first_name}")
        else:
            await message.reply_text("⚠️ هذا الأمر للمطور الأساسي فقط.")
    elif text_clean.startswith("رفع مميز"):
        if role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
            if reply:
                set_user_role(target_user.id, "vip")
                await message.reply_text(f"⭐ تم رفعه (عضو مميز بنجاح): {target_user.first_name}")
        else:
            await message.reply_text("⚠️ هذا الأمر للأدمن والمطورين فقط.")
            
    # أوامر التنزيل
    elif text_clean.startswith("تنزيل ادمن") or text_clean.startswith("تنزيل أدمن"):
        if role_title in ["المطور الاساسي", "مطور أساسي"]:
            if reply:
                set_user_role(target_user.id, "user")
                await message.reply_text(f"👤 تم تنزيله من الإدارة: {target_user.first_name}")
    elif text_clean.startswith("تنزيل مميز"):
        if role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
            if reply:
                set_user_role(target_user.id, "user")
                await message.reply_text(f"⭐ تم تنزيله من المميزين: {target_user.first_name}")

    # أوامر الطرد، الكتم، وإلغاء الكتم
    elif text_clean.startswith("طرد"):
        if role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
            if reply:
                try:
                    await chat.ban_member(target_user.id)
                    await message.reply_text(f"🚫 تم طرد المستخدم: {target_user.first_name}")
                except Exception:
                    await message.reply_text("عذراً، تأكد من صلاحيات البوت الإدارية في المجموعة.")
        else:
            await message.reply_text("⚠️ الأمر مخصص للإدارة فقط.")
                
    elif text_clean.startswith("كتم"):
        if role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
            if reply:
                try:
                    await context.bot.restrict_chat_member(chat.id, target_user.id, permissions={"can_send_messages": False})
                    await message.reply_text(f"🔇 تم كتم المستخدم: {target_user.first_name}")
                except Exception:
                    await message.reply_text("عذراً، تأكد من صلاحيات البوت الإدارية في المجموعة.")
        else:
            await message.reply_text("⚠️ الأمر مخصص للإدارة فقط.")

    elif text_clean.startswith("فتح الكتم") or text_clean.startswith("الغاء كتم"):
        if role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
            if reply:
                try:
                    await context.bot.restrict_chat_member(
                        chat.id, 
                        target_user.id, 
                        permissions={
                            "can_send_messages": True, 
                            "can_send_media_messages": True, 
                            "can_send_other_messages": True, 
                            "can_add_web_page_previews": True
                        }
                    )
                    await message.reply_text(f"🔊 تم إلغاء كتم المستخدم: {target_user.first_name}")
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

    logger.info("Starting bot via Webhook and ready for millions of features...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
