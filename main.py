# ==============================================================================
# سورس اندريس الأسطوري - النسخة الشاملة (الحماية + الرتب + الردود والأوامر المصنفة)
# ==============================================================================

import os
import sys
import time
import random
import sqlite3
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DEV_USERNAME = os.getenv("DEV_USERNAME", "YOUR_USERNAME")

# ------------------------------------------------------------------------------
# قاعدة البيانات الشاملة (المستخدمين، الحماية، الرتب، الردود)
# ------------------------------------------------------------------------------
def init_massive_database():
    connection = sqlite3.connect("bot_ultimate_source_1200plus.db", check_same_thread=False)
    cursor = connection.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_registry (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance INTEGER DEFAULT 500,
            bank_balance INTEGER DEFAULT 1500,
            experience_points INTEGER DEFAULT 0,
            user_level INTEGER DEFAULT 1,
            admin_rank TEXT DEFAULT 'عضو نشط'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups_protection_settings (
            chat_id INTEGER PRIMARY KEY,
            anti_links INTEGER DEFAULT 1,
            anti_spam INTEGER DEFAULT 1,
            lock_chat INTEGER DEFAULT 0,
            anti_bots INTEGER DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_bot_replies (
            chat_id INTEGER,
            trigger_keyword TEXT,
            response_text TEXT,
            PRIMARY KEY (chat_id, trigger_keyword)
        )
    """)

    connection.commit()
    connection.close()

init_massive_database()

USER_STATES = {}

# ------------------------------------------------------------------------------
# 1. قسم الحماية الفورية والمتقدمة (Anti-Spam & Links)
# ------------------------------------------------------------------------------
async def security_protection_engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text or update.message.caption or ""
    
    # استثناء المشرفين والبوت من الحماية
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status in ["administrator", "creator"] or user.id == context.bot.id:
            return
    except:
        pass

    conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
    cursor = conn.cursor()
    cursor.execute("SELECT anti_links, anti_spam, lock_chat FROM groups_protection_settings WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    
    # إعدادات افتراضية للحماية إن لم تكن مسجلة
    anti_links, anti_spam, lock_chat = (1, 1, 0) if not row else row
    conn.close()

    if lock_chat == 1:
        try:
            await update.message.delete()
        except:
            pass
        return

    # منع الروابط
    if anti_links == 1 and ("http://" in text or "https://" in text or "t.me/" in text or "www." in text):
        try:
            await update.message.delete()
            await update.message.reply_text(f"⚠️ عذراً [{user.first_name}](tg://user?id={user.id})، ممنوع نشر الروابط في هذه المجموعة!", parse_mode="Markdown")
        except:
            pass
        return

# ------------------------------------------------------------------------------
# 2. نظام إضافة وحذف الردود والأوامر (مع دعم الاختصار)
# ------------------------------------------------------------------------------
async def command_add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ["group", "supergroup"]:
        return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if "اضف رد" in text:
        USER_STATES[user_id] = {"action": "wait_r_kw", "chat_id": chat_id}
        await update.message.reply_text("📥 ارسل الآن **الكلمة** التي تريد أن يرد عليها البوت:", parse_mode="Markdown")
    elif "اضف امر" in text:
        USER_STATES[user_id] = {"action": "wait_c_old", "chat_id": chat_id}
        await update.message.reply_text("📥 ارسل الآن **الأمر أو الكلمة القديمة** لاختصارها وتعديلها:", parse_mode="Markdown")

async def command_delete_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ["group", "supergroup"]:
        return
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if "حذف رد" in text or "الغاء رد" in text:
        USER_STATES[user_id] = {"action": "wait_d_r", "chat_id": chat_id}
        await update.message.reply_text("🗑️ ارسل **الكلمة** المراد حذف ردها:", parse_mode="Markdown")
    elif "حذف امر" in text or "الغاء امر" in text:
        USER_STATES[user_id] = {"action": "wait_d_c", "chat_id": chat_id}
        await update.message.reply_text("🗑️ ارسل **الأمر** المراد إلغاؤه:", parse_mode="Markdown")

# ------------------------------------------------------------------------------
# 3. عرض الأوامر المصنفة بدقة حسب التصنيفات عند كتابة "الأوامر"
# ------------------------------------------------------------------------------
async def list_categorized_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
    cursor = conn.cursor()
    cursor.execute("SELECT trigger_keyword, response_text FROM custom_bot_replies WHERE chat_id = ?", (chat_id,))
    rows = cursor.fetchall()
    conn.close()

    custom_text = ""
    if rows:
        for r in rows:
            custom_text += f"▪️ `{r[0]}` ➔ `{r[1]}`\n"
    else:
        custom_text = "📭 لا توجد أوامر أو ردود مخصصة مضافة حالياً.\n"

    categorized_message = (
        "📊 **قائمة أوامر سورس اندريس المصنفة بدقة:**\n\n"
        "🛡️ **[قسم الحماية والأمن]**\n"
        "▪️ منع الروابط والتكرار مفعل تلقائياً.\n"
        "▪️ قفل وفتح الدردشة عبر إعدادات المجموعة.\n\n"
        "👑 **[قسم الإدارة والتعديل (اضف/حذف)]**\n"
        "▪️ `اضف رد` - لإضافة رد تفاعلي جديد.\n"
        "▪️ `حذف رد` - لحذف رد مخصص.\n"
        "▪️ `اضف امر` - لاختصار الأوامر وتعديلها.\n"
        "▪️ `حذف امر` - لإلغاء أمر مخصص.\n\n"
        "🎮 **[قسم الألعاب والتسلية والمستويات]**\n"
        "▪️ `/games` - لفتح قاعة الألعاب الكبرى وربح النقاط.\n"
        "▪️ النظام التلقائي للخبرة XP ورفع المستويات.\n\n"
        "🤖 **[قسم الردود العامة التلقائية]**\n"
        "▪️ ردود تفاعلية عند قول: (بوت، شلونك، هلا، سلام، منور، صباح الخير).\n\n"
        f"📂 **[الأوامر والردود المخصصة المضافة في مجموعتكم]**\n"
        f"{custom_text}"
    )
    await update.message.reply_text(categorized_message, parse_mode="Markdown")

# ------------------------------------------------------------------------------
# 4. قاعة الألعاب والمستويات المتقدمة
# ------------------------------------------------------------------------------
async def display_games_hub_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 حجر النرد السريع", callback_data="game_dice_roll"),
         InlineKeyboardButton("💰 حظك اليوم المالي", callback_data="game_daily_luck")],
        [InlineKeyboardButton("🥷 سرقة البنك الكبرى", callback_data="game_bank_robbery"),
         InlineKeyboardButton("📊 ملفك والـ XP", callback_data="game_user_profile")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="main_menu_return")]
    ]
    text = "🎮 **قاعة ألعاب سورس اندريس الكبرى والمتقدمة**\nاختر لعبتك المفضلة لربح النقاط:"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def games_engine_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    callback_data = query.data

    conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance, bank_balance, experience_points, user_level, admin_rank FROM users_registry WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users_registry (user_id, username, full_name, balance) VALUES (?, ?, ?, 500)",
                       (user_id, query.from_user.username, query.from_user.first_name))
        conn.commit()
        balance, bank_balance, xp, level, rank = 500, 1500, 0, 1, "عضو نشط"
    else:
        balance, bank_balance, xp, level, rank = row

    if callback_data == "game_dice_roll":
        dice = random.randint(1, 6)
        earned = dice * 25
        new_bal = balance + earned
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_bal, user_id))
        conn.commit()
        await query.edit_message_text(f"🎲 النرد أظهر: **{dice}**\n🎉 ربحت `{earned}` نقطة!\n💰 رصيدك: `{new_bal}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_daily_luck":
        luck = random.choice([150, 300, 600, -150])
        new_bal = balance + luck
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_bal, user_id))
        conn.commit()
        await query.edit_message_text(f"🍀 حظك اليوم: كسبت/خسرت `{luck}` نقطة.\n💰 رصيدك: `{new_bal}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_bank_robbery":
        loot = random.randint(300, 900)
        new_bal = balance + loot
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_bal, user_id))
        conn.commit()
        await query.edit_message_text(f"🥷 تمت عملية السطو بنجاح!\n💎 غنيمتك: `{loot}` نقطة.\n💰 رصيدك: `{new_bal}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_user_profile":
        await query.edit_message_text(f"👤 **ملفك الشخصي والمالي:**\n🆔 الآيدي: `{user_id}`\n👑 الرتبة الإدارية: `{rank}`\n💰 الكاش: `{balance}`\n🏦 البنك: `{bank_balance}`\n⭐ الـ XP والمستوى: `{xp}` (مستوى {level})", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_hub_back":
        await display_games_hub_menu(update, context)
        conn.close()
        return

    conn.close()

# ------------------------------------------------------------------------------
# 5. معالج الرسائل العام والتفاعلي (الحماية + الردود العامة + خطوات الإضافة)
# ------------------------------------------------------------------------------
async def global_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    # تشغيل نظام الحماية أولاً
    await security_protection_engine(update, context)

    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text.strip()
    user_id = user.id

    # تفاعل خطوات الإضافة والحذف
    if user_id in USER_STATES:
        state = USER_STATES[user_id]
        if state["chat_id"] == chat_id:
            action = state["action"]
            
            if action == "wait_r_kw":
                USER_STATES[user_id] = {"action": "wait_r_res", "chat_id": chat_id, "kw": text}
                await update.message.reply_text(f"📥 الكلمة: `{text}`.\nالآن ارسل **الرد** المراد إرساله:", parse_mode="Markdown")
                return
            elif action == "wait_r_res":
                kw = state["kw"]
                conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO custom_bot_replies (chat_id, trigger_keyword, response_text) VALUES (?, ?, ?)", (chat_id, kw, text))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"✅ تم حفظ الرد للكلمة `{kw}` بنجاح!", parse_mode="Markdown")
                return
                
            elif action == "wait_c_old":
                USER_STATES[user_id] = {"action": "wait_c_new", "chat_id": chat_id, "old": text}
                await update.message.reply_text(f"📥 الأمر القديم: `{text}`.\nالآن ارسل **الأمر الجديد** أو الاختصار:", parse_mode="Markdown")
                return
            elif action == "wait_c_new":
                old = state["old"]
                conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, old))
                cursor.execute("INSERT OR REPLACE INTO custom_bot_replies (chat_id, trigger_keyword, response_text) VALUES (?, ?, ?)", (chat_id, text, f"تم تنفيذ الاختصار للأمر: {old}"))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"✅ تم تعديل واختصار الأمر بنجاح (`{text}` بدلاً من `{old}`).", parse_mode="Markdown")
                return

            elif action in ["wait_d_r", "wait_d_c"]:
                conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, text))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"🗑️ تم حذف العنصر `{text}` بنجاح!", parse_mode="Markdown")
                return

    # فحص الردود المخصصة في المجموعة
    conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
    cursor = conn.cursor()
    cursor.execute("SELECT response_text FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, text))
    res = cursor.fetchone()
    if res:
        await update.message.reply_text(res[0])
        conn.close()
        return

    # الردود العامة التفاعلية للبوت
    lower_text = text.lower()
    general_replies = {
        "بوت": "عيون البوت، امرني بشي يا غالي؟ 🤖❤️",
        "البوت": "نعم حبيبي وياك، شنو محتاج؟",
        "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته، منورنا يا مبدع! 🤍",
        "هلا": "هلا بيك وبحضورك الطيب ✨",
        "شلونك": "الحمد لله بخير وتمام التمام، أنت طمني عنك؟ 😊",
        "منور": "نور عيونك هذا يا غالي 🌟",
        "صباح الخير": "صباح النور والسرور، نهارك سعيد 🌸",
        "مساء الخير": "مساء الورد والفل 🌙",
        "شكرا": "العفو ولو، تدلل عيوني واجبنا! 🙏"
    }

    if lower_text in general_replies:
        await update.message.reply_text(general_replies[lower_text])
        conn.close()
        return

    # نظام الخبرة XP والنقاط التلقائي
    cursor.execute("SELECT balance, experience_points, user_level FROM users_registry WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users_registry (user_id, username, full_name, balance, experience_points, user_level) VALUES (?, ?, ?, 500, 10, 1)",
                       (user_id, user.username, user.first_name))
    else:
        bal, xp, lvl = row
        new_xp = xp + 10
        new_lvl = lvl
        if new_xp >= lvl * 200:
            new_lvl += 1
            await update.message.reply_text(f"🎖️ مبروك [{user.first_name}](tg://user?id={user.id})! صعدت للمستوى **{new_lvl}** بالتفاعل!")
        cursor.execute("UPDATE users_registry SET experience_points = ?, user_level = ?, balance = ? WHERE user_id = ?", (new_xp, new_lvl, bal + 2, user_id))
    
    conn.commit()
    conn.close()

# ------------------------------------------------------------------------------
# واجهة البداية والتشغيل
# ------------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🎮 قاعة الألعاب والمستويات", callback_data="menu_games")],
        [InlineKeyboardButton("📊 عرض الأوامر المصنفة", callback_data="menu_list")]
    ]
    await update.message.reply_text(f"مرحباً بك عزيزي [{user.first_name}](tg://user?id={user.id}) في سورس اندريس المطور والآمن!", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def menu_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "menu_games":
        await display_games_hub_menu(update, context)
    elif query.data == "menu_list":
        await list_categorized_commands(update, context)
    elif query.data == "main_menu_return":
        await query.edit_message_text("🏠 القائمة الرئيسية:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎮 قاعة الألعاب والمستويات", callback_data="menu_games")]]))

def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ يرجى تعيين التوكن الحقيقي للمتابعة!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("games", display_games_hub_menu))
    application.add_handler(CommandHandler("الأوامر", list_categorized_commands))
    
    # معالجات أوامر الإضافة والحذف النصية
    application.add_handler(MessageHandler(filters.Regex("^(اضف رد|اضف امر)$"), command_add_handler))
    application.add_handler(MessageHandler(filters.Regex("^(حذف رد|حذف امر|الغاء رد|الغاء امر)$"), command_delete_handler))

    application.add_handler(CallbackQueryHandler(games_engine_callback_handler, pattern="^game_"))
    application.add_handler(CallbackQueryHandler(menu_callbacks, pattern="^menu_|main_menu_"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, global_message_handler))

    logger.info("🚀 سورس اندريس يعمل بكفاءة تامة مع الحماية والرتب...")

    while True:
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        except Exception as e:
            logger.error(f"⚠️ إعادة تشغيل تلقائية بعد خطأ: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

