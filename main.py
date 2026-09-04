# ==============================================================================
# سورس اندريس الأسطوري - النسخة العملاقة والمتكاملة (بدون حذف أي ميزة قديمة)
# يحتوي على نظام الألعاب، المتجر، الحماية، ونظام "اضف/الغاء امر" التفاعلي
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

# ------------------------------------------------------------------------------
# إعدادات التسجيل واللوغ (Logging Configuration)
# ------------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DEV_USERNAME = os.getenv("DEV_USERNAME", "YOUR_USERNAME")

# ------------------------------------------------------------------------------
# هيكلة وتصميم قاعدة البيانات الشاملة (SQLite Massive Core)
# ------------------------------------------------------------------------------
def init_massive_database():
    database_name = "bot_ultimate_source_1200plus.db"
    connection = sqlite3.connect(database_name, check_same_thread=False)
    cursor = connection.cursor()
    
    # جدول المستخدمين الشامل والنقاط
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_registry (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance INTEGER DEFAULT 500,
            bank_balance INTEGER DEFAULT 1500,
            experience_points INTEGER DEFAULT 0,
            user_level INTEGER DEFAULT 1,
            warnings_count INTEGER DEFAULT 0,
            reputation INTEGER DEFAULT 0,
            spouse_id INTEGER DEFAULT 0,
            is_banned_globally INTEGER DEFAULT 0,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول إعدادات المجموعات والحماية المتقدمة
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups_protection_settings (
            chat_id INTEGER PRIMARY KEY,
            anti_links INTEGER DEFAULT 1,
            anti_spam_flood INTEGER DEFAULT 1,
            anti_arabic_spam INTEGER DEFAULT 0,
            anti_bots_join INTEGER DEFAULT 1,
            anti_forwards INTEGER DEFAULT 0,
            anti_media_spam INTEGER DEFAULT 0,
            lock_group_chat INTEGER DEFAULT 0,
            welcome_message TEXT DEFAULT 'أهلاً بك عزيزي العضو في قصر المملكة العريق!'
        )
    """)
    
    # جدول الردود والمميزات المخصصة (اضف امر / الغاء امر)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_bot_replies (
            chat_id INTEGER,
            trigger_keyword TEXT,
            response_text TEXT,
            PRIMARY KEY (chat_id, trigger_keyword)
        )
    """)
    
    # جدول المشرفين المخصصين والرتب الإدارية
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_bot_admins (
            user_id INTEGER PRIMARY KEY,
            admin_rank_title TEXT
        )
    """)
    
    # جدول قائمة الحظر العام للمخربين
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_blacklisted_users (
            user_id INTEGER PRIMARY KEY,
            ban_reason TEXT
        )
    """)
    
    # جدول المتجر والرتب المشتراة
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_shop_inventory (
            user_id INTEGER,
            item_name TEXT,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

init_massive_database()

def verify_developer_privileges(user_id: int, username: str) -> bool:
    if username and username.lower() == DEV_USERNAME.lower():
        return True
    conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM custom_bot_admins WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

# ------------------------------------------------------------------------------
# نظام "أضف أمر" و "الغاء أمر" الذكي والتفاعلي
# ------------------------------------------------------------------------------
USER_STATE_ADD_COMMAND = {}

async def command_add_custom_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ["group", "supergroup"]:
        await update.message.reply_text("⚠️ هذا الأمر يعمل داخل المجموعات فقط!")
        return
    
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ يرجى كتابة الأمر المراد إضافته.\nمثال: `اضف امر طرد`", parse_mode="Markdown")
        return
    
    command_name = args[0]
    USER_STATE_ADD_COMMAND[user_id] = {"cmd": command_name, "chat_id": update.effective_chat.id}
    await update.message.reply_text(f"📥 حسناً، لقد اخترت الأمر: **{command_name}**.\nالآن قم بإرسال الكلمة أو الرد أو الاختصار الذي تريد اعتماده له:", parse_mode="Markdown")

async def command_remove_custom_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat.type in ["group", "supergroup"]:
        return
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ يرجى كتابة الأمر المراد إلغاؤه.\nمثال: `الغاء امر طرد`", parse_mode="Markdown")
        return
    
    command_name = args[0]
    chat_id = update.effective_chat.id
    
    conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, command_name))
    conn.commit()
    conn.close()
    
    await update.message.reply_text(f"🗑️ تم إلغاء وحذف الأمر `{command_name}` بنجاح من هذه المجموعة!", parse_mode="Markdown")

async def list_custom_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
    cursor = conn.cursor()
    cursor.execute("SELECT trigger_keyword, response_text FROM custom_bot_replies WHERE chat_id = ?", (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        await update.message.reply_text("📭 لا توجد أي أوامر مخصصة مضافة في هذه المجموعة حالياً.")
        return
    
    text = "📜 **قائمة الأوامر المخصصة في المجموعة:**\n\n"
    for r in rows:
        text += f"🔹 أمر: `{r[0]}` ➔ الرد: `{r[1]}`\n"
    await update.message.reply_text(text, parse_mode="Markdown")

# ------------------------------------------------------------------------------
# نظام الألعاب والتسلية المتقدم والمتكامل (Games Sub-System)
# ------------------------------------------------------------------------------
async def display_games_hub_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 حجر النرد السريع", callback_data="game_dice_roll"),
         InlineKeyboardButton("🎯 رمي السهم بدقة", callback_data="game_dart_throw")],
        [InlineKeyboardButton("⚽ ركلات الجزاء", callback_data="game_football_shoot"),
         InlineKeyboardButton("🎰 ماكينة الحظ (سلوتس)", callback_data="game_slots_spin")],
        [InlineKeyboardButton("💰 حظك اليوم المالي", callback_data="game_daily_luck"),
         InlineKeyboardButton("🥷 سرقة البنك الكبرى", callback_data="game_bank_robbery")],
        [InlineKeyboardButton("🪙 طش و صك (عملة)", callback_data="game_coin_flip"),
         InlineKeyboardButton("📊 ملفك المالي الشامل", callback_data="game_user_profile")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu_return")]
    ]
    text = "🎮 **قاعة ألعاب سورس اندريس الكبرى والمتقدمة**\nاختر لعبتك المفضلة لربح النقاط والأموال ومضاعفة رصيدك:"
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
    cursor.execute("SELECT balance, bank_balance, experience_points, user_level FROM users_registry WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users_registry (user_id, username, full_name) VALUES (?, ?, ?)",
                       (user_id, query.from_user.username, query.from_user.first_name))
        conn.commit()
        balance, bank_balance, xp, level = 500, 1500, 0, 1
    else:
        balance, bank_balance, xp, level = row

    if callback_data == "game_dice_roll":
        if balance < 30:
            await query.edit_message_text("❌ رصيدك الكاش لا يكفي! تحتاج إلى 30 نقطة على الأقل.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))
            conn.close()
            return
        dice_result = random.randint(1, 6)
        earned_prize = dice_result * 20
        new_balance = balance - 30 + earned_prize
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        conn.commit()
        await query.edit_message_text(f"🎲 رميت النرد وظهر الرقم: **{dice_result}**\n🎉 ربحت: `{earned_prize}` نقطة!\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_daily_luck":
        luck_modifier = random.choice([-200, 50, 150, 300, 600, 1200, -250])
        new_balance = balance + luck_modifier
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        conn.commit()
        if luck_modifier > 0:
            await query.edit_message_text(f"🍀 حظك ممتاز اليوم! ربحت **{luck_modifier}** نقطة.\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))
        else:
            await query.edit_message_text(f"💀 حظك سيء للأسف! خسرت **{abs(luck_modifier)}** نقطة.\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_bank_robbery":
        if balance < 60:
            await query.edit_message_text("❌ تحتاج إلى 60 نقطة كاش لتدبير تفاصيل عملية السرقة.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))
            conn.close()
            return
        is_successful = random.choice([True, False, True])
        if is_successful:
            stolen_loot = random.randint(250, 950)
            new_balance = balance + stolen_loot
            cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_balance, user_id))
            conn.commit()
            await query.edit_message_text(f"🥷 تمت عملية السطو على البنك بنجاح تام!\n💎 غنيمتك: `{stolen_loot}` نقطة.\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))
        else:
            new_balance = balance - 60
            cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_balance, user_id))
            conn.commit()
            await query.edit_message_text(f"🚨 فشلت خطة السرقة وقبض عليك الحراس!\n💸 غرامة مالية: 60 نقطة.\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_coin_flip":
        coin_side = random.choice(["صورة الملك", "كتابة التاريخ"])
        prize_val = 120
        new_balance = balance + prize_val
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        conn.commit()
        await query.edit_message_text(f"🪙 استقرت العملة المعدنية على وجه: **{coin_side}**\n🎉 ربحت `{prize_val}` نقطة في رصيدك!\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_user_profile":
        profile_string = (
            f"👤 **ملفك الشخصي والمالي الشامل:**\n\n"
            f"🆔 الآيدي الشخصي: `{user_id}`\n"
            f"📛 الاسم المسجل: {query.from_user.first_name}\n"
            f"💰 الكاش المتاح: `{balance}` نقطة\n"
            f"🏦 رصيد البنك: `{bank_balance}` نقطة\n"
            f"⭐ نقاط الخبرة XP: `{xp}`\n"
            f"🎖️ مستواك الحالي: `{level}`"
        )
        await query.edit_message_text(profile_string, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_hub_back":
        await display_games_hub_menu(update, context)
        conn.close()
        return

    conn.close()

# ------------------------------------------------------------------------------
# نظام الردود والرسائل العالمي (مع معالجة الأوامر المخصصة)
# ------------------------------------------------------------------------------
async def global_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text

    # التحقق من حالة إضافة أمر جديد (تفاعلي)
    if user.id in USER_STATE_ADD_COMMAND:
        cmd_data = USER_STATE_ADD_COMMAND[user.id]
        target_chat = cmd_data["chat_id"]
        command_name = cmd_data["cmd"]
        
        if chat_id == target_chat:
            conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO custom_bot_replies (chat_id, trigger_keyword, response_text) VALUES (?, ?, ?)",
                           (chat_id, command_name, text))
            conn.commit()
            conn.close()
            
            del USER_STATE_ADD_COMMAND[user.id]
            await update.message.reply_text(f"✅ تم بنجاح ربط الأمر `{command_name}` بالرد الجديد (`{text}`)!", parse_mode="Markdown")
            return

    # فحص الأوامر المخصصة المحفوظة
    conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
    cursor = conn.cursor()
    cursor.execute("SELECT response_text FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, text))
    res = cursor.fetchone()
    
    if res:
        await update.message.reply_text(res[0])
        conn.close()
        return

    # نظام الخبرة XP والنقاط التلقائي عند التفاعل
    cursor.execute("SELECT balance, experience_points, user_level FROM users_registry WHERE user_id = ?", (user.id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users_registry (user_id, username, full_name, balance, experience_points, user_level) VALUES (?, ?, ?, 500, 10, 1)",
                       (user.id, user.username, user.first_name))
    else:
        bal, xp, lvl = row
        new_xp = xp + 10
        new_bal = bal + 3
        new_lvl = lvl
        if new_xp >= lvl * 200:
            new_lvl += 1
            await update.message.reply_text(f"🎖️ مبروك [{user.first_name}](tg://user?id={user.id})! صعدت للمستوى **{new_lvl}** في التفاعل!", parse_mode="Markdown")
        cursor.execute("UPDATE users_registry SET balance = ?, experience_points = ?, user_level = ? WHERE user_id = ?", (new_bal, new_xp, new_lvl, user.id))
    
    conn.commit()
    conn.close()

# ------------------------------------------------------------------------------
# واجهة البداية والتشغيل الرئيسية
# ------------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🎮 قاعة الألعاب والتسلية", callback_data="menu_games"),
         InlineKeyboardButton("📜 أوامر الإدارة والمميزات", callback_data="menu_help")]
    ]
    welcome_msg = f"مرحباً بك عزيزي [{user.first_name}](tg://user?id={user.id}) في النسخة العملاقة والمطورة من **سورس اندريس**!"
    await update.message.reply_text(welcome_msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def main_menu_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "menu_games":
        await display_games_hub_menu(update, context)
    elif data == "menu_help":
        help_text = (
            "📜 **دليل أوامر سورس اندريس الشامل:**\n\n"
            "🔹 `اضف امر [الاسم]` - لإضافة أمر جديد وتخصيص رده.\n"
            "🔹 `الغاء امر [الاسم]` - لحذف الأمر المخصص.\n"
            "🔹 `الأوامر` - لعرض كافة الأوامر المخصصة في المجموعة.\n"
            "🔹 `/games` - لفتح قاعة الألعاب الكبرى.\n"
        )
        await query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu_return")]]), parse_mode="Markdown")
    elif data == "main_menu_return":
        user = query.from_user
        keyboard = [
            [InlineKeyboardButton("🎮 قاعة الألعاب والتسلية", callback_data="menu_games"),
             InlineKeyboardButton("📜 أوامر الإدارة والمميزات", callback_data="menu_help")]
        ]
        await query.edit_message_text("🏠 القائمة الرئيسية لسورس اندريس:", reply_markup=InlineKeyboardMarkup(keyboard))

# ------------------------------------------------------------------------------
# نقطة التشغيل الرئيسية مع حلقة منع التوقف (Anti-Crash Loop)
# ------------------------------------------------------------------------------
def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ يرجى تعيين توكن البوت الحقيقي داخل متغير TOKEN قبل التشغيل!")
        return

    application = Application.builder().token(TOKEN).build()

    # الأوامر
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("games", display_games_hub_menu))
    application.add_handler(CommandHandler("الأوامر", list_custom_commands))
    application.add_handler(CommandHandler("اضف", command_add_custom_trigger))
    application.add_handler(CommandHandler("الغاء", command_remove_custom_trigger))
    application.add_handler(MessageHandler(filters.Regex("^اضف امر"), command_add_custom_trigger))
    application.add_handler(MessageHandler(filters.Regex("^الغاء امر"), command_remove_custom_trigger))

    # الكول باك
    application.add_handler(CallbackQueryHandler(games_engine_callback_handler, pattern="^game_"))
    application.add_handler(CallbackQueryHandler(main_menu_callbacks, pattern="^menu_|main_menu_"))

    # معالج الرسائل
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, global_message_handler))

    logger.info("🚀 سورس اندريس العملاق يعمل الآن بكفاءة تامة 24/7 مع نظام الأوامر المخصصة...")

    # حلقة الحراسة والتشغيل التلقائي لمنع التوقف نهائياً
    while True:
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        except Exception as e:
            logger.error(f"⚠️ حدث انقطاع، جاري إعادة التشغيل خلال 5 ثوانٍ: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
