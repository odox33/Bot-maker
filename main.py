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

# --- معالجة الأوامر والميزات داخل المجموعات والرسائل ---
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
            await message.reply_text("✅ **تم تفعيل البوت وحمايته وألعابه بالكامل في هذه المجموعة!**\nاكتب `الأوامر` أو `الالعاب` لعرض القوائم الفورية.")
            return

    if chat.type not in ["group", "supergroup"]:
        # إذا أرسل المستخدم رسالة خاصة للبوت
        if text_clean == "/start":
            await message.reply_text("أهلاً بك! هذا البوت يعمل مباشرة داخل **المجموعات**.\nأضفني إلى مجموعتك واكتب **تفعيل** للبدء.")
        return

    role_title = get_user_role(user.id, user.username)
    reply = message.reply_to_message
    target_user = reply.from_user if reply else user
    target_role = get_user_role(target_user.id, target_user.username)

    # 2. قوائم الاختصارات المباشرة داخل الكروب (تظهر فوراً بالكروب دون دخول البوت)
    if text_clean in ["الالعاب", "الألعاب", "ألعاب", "قسم الالعاب"]:
        games_text = (
            "🎮 **قائمة ألعاب المجموعة الشاملة:**\n\n"
            "🎲 `روليت` - عجلة حظ ونقاط\n"
            "🕵️‍♂️ `مافيا` - لعبة التصويت والذكاء\n"
            "🪑 `كراسي` أو `لعبة الكراسي` - أسرع من يجلس\n"
            "🙈 `غميضة` - البحث والاختفاء\n"
            "🧠 `لغز` - اختبار ذكاء ومعلومات\n"
            "🍻 `صراحة` - أسئلة جريئة وممتعة\n"
            "⚔️ `تحدي` - منافسة عشوائية بين الأعضاء\n\n"
            "👉 *فقط اكتب اسم اللعبة في الكروب للبدء فورا!*"
        )
        await message.reply_text(games_text)
        return

    if text_clean in ["الأوامر", "اوامر", "قائمة الأوامر", "الاوامر"]:
        commands_text = (
            "📜 **دليل أوامر البوت الشامل في المجموعة:**\n\n"
            "📊 **الإحصائيات والمعلومات:**\n"
            "- `ايدي` أو `ايديك` (عرض معلوماتك ونقاطك وسحكاتك)\n"
            "- `رتبتي` (معرفة رتبتك الحالية)\n"
            "- `الاحصائيات` (عرض إحصائيات الرسائل والنقاط)\n\n"
            "🛡️ **الإدارة والحماية:**\n"
            "- `رفع ادمن` / `تنزيل ادمن` (بالرد على الشخص)\n"
            "- `رفع مميز` / `تنزيل مميز` (بالرد على الشخص)\n"
            "- `طرد` (طرد العضو المخالف)\n"
            "- `كتم` / `فتح الكتم` (إيقاف أو السماح بالكتابة)\n\n"
            "🎮 **قسم التسلية والألعاب:**\n"
            "- اكتب `الالعاب` لإظهار لوحة الألعاب الكاملة.\n"
            "- `المتجر` (لعرض خدمات وترقيات المجموعة)."
        )
        await message.reply_text(commands_text)
        return

    # 3. الألعاب الفورية داخل الكروب
    if text_clean in ["روليت", "لعبة روليت"]:
        lucky_points = random.randint(15, 120)
        await message.reply_text(f"🎲 **عجلة روليت الحظ:**\nدارت العجلة وفاز البطل **{user.first_name}** بـ **{lucky_points}** نقطة مضافة لرصيده!")
        return
    elif text_clean in ["مافيا", "لعبة مافيا"]:
        await message.reply_text("🕵️‍♂️ **لعبة المافيا:**\nبدأت جولة المافيا والتصويت السري! من هو القاتل الخفي بينكم؟ شاركوا بالنقاش.")
        return
    elif text_clean in ["لعبة الكراسي", "كراسي"]:
        await message.reply_text("🪑 **بدأت لعبة الكراسي الموسيقية!**\nتوقف الموسيقى.. أسرع واكتب `جلس` لتحجز مقعدك الفائز!")
        return
    elif text_clean == "جلس":
        await message.reply_text(f"🪑 كفوو! الكابتن **{user.first_name}** أسرع وجلس على الكرسي وحصد النقطة!")
        return
    elif text_clean in ["غميضة", "لعبة غميضة"]:
        await message.reply_text("🙈 **لعبة الغميضة:**\nتم تشتت الأعضاء في أرجاء المجموعة، ابدأوا بالبحث عن بعضكم!")
        return
    elif text_clean in ["لغز", "حزورة"]:
        puzzles = [
            ("ما هو الشيء الذي يحرق نفسه ليضيء غيرك؟", "الشمعة"),
            ("من هو الوالي الذي قُتل ولم يكن من الجن أو الإنس؟", "كبش فداء / ليس حقيقي"),
            ("ما هو الشيء الذي كلما أخذت منه كبر وكلما وضعت فيه صغر؟", "الحفرة")
        ]
        chosen = random.choice(puzzles)
        await message.reply_text(f"🧠 **لغز وتحدي:**\n{chosen[0]}\n*(أسرع شخص يكتب الإجابة يفوز بنقاط مضاعفة!)*")
        return
    elif text_clean in ["صراحة", "لعبة صراحة"]:
        questions = [
            "ما هي أكثر صفة تكرهها في الشخص المقابل لك؟",
            "موقف محرج صار معك وماتنساه؟",
            "لو ملكت العالم ليوم واحد، ماذا ستفعل أولاً؟",
            "كلمة تعتذر فيها لمن؟ ولمن تقول شكراً؟"
        ]
        await message.reply_text(f"🍻 **سؤال صراحة:**\n{random.choice(questions)}")
        return

    # 4. إحصائيات ومتجر الكروب
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

    if text_clean in ["رتبتي", "الرتبة"]:
        await message.reply_text(f"- : رتبتك الحالية في المجموعة : ( {target_role} )")
        return

    if text_clean in ["الاحصائيات", "إحصائياتي"]:
        stats = get_user_stats_data(target_user.id)
        await message.reply_text(f"📊 **إحصائيات الأعضاء ({target_user.first_name}):**\n💬 الرسائل: {stats[0]}\n⭐ النقاط الكلية: {stats[1]}\n📸 الصور: {stats[2]}\n🏆 المستوى: {stats[4]}")
        return

    if text_clean in ["المتجر", "shop"]:
        await message.reply_text("🛍️ **متجر مجموعة البوت:**\n1. شراء تميز أسبوعي (50 نقطة)\n2. تصفية سجل السحكات (30 نقطة)\n3. تمييز الاسم بلون مميز (40 نقطة)\n*تواصل مع إدارة الكروب لتفعيل مشترياتك النقاطية.*")
        return

    # 5. أوامر الإدارة والصلاحيات (بالرد على الرسالة)
    if text_clean.startswith("رفع مطور أساسي") and role_title == "المطور الاساسي":
        if reply:
            set_user_role(target_user.id, "dev")
            await message.reply_text(f"👤 تم رفعه (مطور أساسي بنجاح): {target_user.first_name}")
    elif text_clean.startswith("رفع ادمن") or text_clean.startswith("رفع أدمن"):
        if role_title in ["المطور الاساسي", "مطور أساسي"]:
            if reply:
                set_user_role(target_user.id, "admin")
                await message.reply_text(f"👤 تم رفعه (أدمن رسمي): {target_user.first_name}")
        else:
            await message.reply_text("⚠️ هذا الأمر للمطور الأساسي فقط.")
    elif text_clean.startswith("رفع مميز"):
        if role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
            if reply:
                set_user_role(target_user.id, "vip")
                await message.reply_text(f"⭐ تم رفعه (عضو مميز): {target_user.first_name}")
        else:
            await message.reply_text("⚠️ للأدمن والمطورين فقط.")
            
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

    # الطرد والكتم
    elif text_clean.startswith("طرد"):
        if role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
            if reply:
                try:
                    await chat.ban_member(target_user.id)
                    await message.reply_text(f"🚫 تم طرد المخالف: {target_user.first_name}")
                except Exception:
                    await message.reply_text("تأكد من صلاحيات البوت للإشراف في المجموعة.")
        else:
            await message.reply_text("⚠️ الأمر مخصص للإدارة.")
                
    elif text_clean.startswith("كتم"):
        if role_title in ["المطور الاساسي", "مطور أساسي", "أدمن"]:
            if reply:
                try:
                    await context.bot.restrict_chat_member(chat.id, target_user.id, permissions={"can_send_messages": False})
                    await message.reply_text(f"🔇 تم كتم العضو: {target_user.first_name}")
                except Exception:
                    await message.reply_text("تأكد من صلاحيات البوت للإشراف في المجموعة.")
        else:
            await message.reply_text("⚠️ الأمر مخصص للإدارة.")

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
                    await message.reply_text(f"🔊 تم فتح الكتم عن: {target_user.first_name}")
                except Exception:
                    await message.reply_text("تأكد من صلاحيات البوت للإشراف في المجموعة.")

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", group_commands_handler))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, group_commands_handler))

    PORT = int(os.environ.get("PORT", "10000"))
    RENDER_URL = "https://bot-maker-1-709e.onrender.com"

    logger.info("Bot started successfully for direct group commands...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
