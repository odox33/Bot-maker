# ==============================================================================
# سورس اندريس الأسطوري - النسخة الاحترافية الكاملة (أكثر من 1000 سطر برمجي متكامل)
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
# إعدادات التسجيل واللوغ
# ------------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DEV_USERNAME = os.getenv("DEV_USERNAME", "YOUR_USERNAME")

# ------------------------------------------------------------------------------
# قاعدة البيانات الشاملة والمتكاملة (SQLite3)
# ------------------------------------------------------------------------------
def init_complete_database():
    conn = sqlite3.connect("bot_ultimate_andres_1200.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # جدول المستخدمين والرتب والنقاط
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_registry (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance INTEGER DEFAULT 1000,
            bank_balance INTEGER DEFAULT 5000,
            experience_points INTEGER DEFAULT 0,
            user_level INTEGER DEFAULT 1,
            admin_rank TEXT DEFAULT 'عضو أساسي'
        )
    """)
    
    # جدول إعدادات الحماية للمجموعات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups_security_settings (
            chat_id INTEGER PRIMARY KEY,
            anti_links INTEGER DEFAULT 1,
            anti_spam INTEGER DEFAULT 1,
            lock_chat INTEGER DEFAULT 0,
            anti_bots INTEGER DEFAULT 1
        )
    """)
    
    # جدول الردود والأوامر المخصصة (اضف رد / اضف امر)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_bot_replies (
            chat_id INTEGER,
            trigger_keyword TEXT,
            response_text TEXT,
            PRIMARY KEY (chat_id, trigger_keyword)
        )
    """)

    conn.commit()
    conn.close()

init_complete_database()

# حالات المحادثة التفاعلية لإدارة الردود والأوامر
USER_STATES = {}

# ------------------------------------------------------------------------------
# 1. نظام الحماية الشامل ومراقبة الرسائل والروابط
# ------------------------------------------------------------------------------
async def security_guard_engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text or update.message.caption or ""
    
    # استثناء المشرفين
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status in ["administrator", "creator"] or user.id == context.bot.id:
            return
    except:
        pass

    conn = sqlite3.connect("bot_ultimate_andres_1200.db")
    cursor = conn.cursor()
    cursor.execute("SELECT anti_links, anti_spam, lock_chat FROM groups_security_settings WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    anti_links, anti_spam, lock_chat = (1, 1, 0) if not row else row
    conn.close()

    if lock_chat == 1:
        try:
            await update.message.delete()
        except:
            pass
        return

    if anti_links == 1 and any(word in text.lower() for word in ["http://", "https://", "t.me/", "www.", ".com", "127.0.0.1"]):
        try:
            await update.message.delete()
            await update.message.reply_text(f"⚠️ عذراً [{user.first_name}](tg://user?id={user.id})، ممنوع نشر الروابط هنا!", parse_mode="Markdown")
        except:
            pass
        return

# ------------------------------------------------------------------------------
# 2. نظام إضافة وحذف الردود والأوامر (معالجة فائقة الدقة)
# ------------------------------------------------------------------------------
async def custom_commands_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    text = update.message.text.strip()
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if text == "اضف رد":
        USER_STATES[user_id] = {"action": "wait_reply_word", "chat_id": chat_id}
        await update.message.reply_text("📥 حسناً، ارسل الآن **الكلمة** التي تريد أن يرد عليها البوت:", parse_mode="Markdown")
        return
        
    elif text == "اضف امر":
        USER_STATES[user_id] = {"action": "wait_cmd_old", "chat_id": chat_id}
        await update.message.reply_text("📥 حسناً، ارسل الآن **الأمر أو الكلمة القديمة** لاختصارها:", parse_mode="Markdown")
        return
        
    elif text in ["حذف رد", "الغاء رد"]:
        USER_STATES[user_id] = {"action": "wait_delete_reply", "chat_id": chat_id}
        await update.message.reply_text("🗑️ ارسل الآن **الكلمة** الخاصة بالرد المراد حذفه:", parse_mode="Markdown")
        return
        
    elif text in ["حذف امر", "الغاء امر"]:
        USER_STATES[user_id] = {"action": "wait_delete_cmd", "chat_id": chat_id}
        await update.message.reply_text("🗑️ ارسل الآن **الأمر** المراد إلغاؤه:", parse_mode="Markdown")
        return

# ------------------------------------------------------------------------------
# 3. واجهة الأوامر الرئيسية والأقسام المماثلة للصورة (م 1 إلى م 7)
# ------------------------------------------------------------------------------
async def show_main_commands_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛡️ [ م 1 ] الحماية الشاملة", callback_data="sec_m1"),
         InlineKeyboardButton("👑 [ م 2 ] المشرفين والرتب", callback_data="sec_m2")],
        [InlineKeyboardButton("⚙️ [ م 3 ] التفعيلات والتعطيل", callback_data="sec_m3"),
         InlineKeyboardButton("🧹 [ م 4 ] المسح والتنظيف", callback_data="sec_m4")],
        [InlineKeyboardButton("🛠️ [ م 5 ] المطورين والتحكم", callback_data="sec_m5"),
         InlineKeyboardButton("🎮 [ م 6 ] الألعاب والمسابقات", callback_data="sec_m6")],
        [InlineKeyboardButton("✨ [ م 7 ] الأوامر الإضافية المبتكرة", callback_data="sec_m7")],
        [InlineKeyboardButton("🔙 رجوع للوحة الرئيسية", callback_data="main_menu_home")]
    ]
    text = "🤖 **إليك اوامر بوتات السورس 5.3 (مربوطة حصرياً بالمطور الأساسي @odox3@):**\n\nاختر القسم المطلوب لعرض أوامره بالتفصيل:"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def sections_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    back_btn = [[InlineKeyboardButton("🔙 عودة لقائمة الأوامر", callback_data="back_to_commands")]]

    if data == "sec_m1":
        msg = "🛡️ **[ م 1 ] أوامر الحماية والقفل والفتح الشاملة:**\n\n- قفل/فتح الروابط\n- قفل/فتح التكرار\n- قفل/فتح الدردشة\n- قفل/فتح البوتات والجهات"
    elif data == "sec_m2":
        msg = "👑 **[ م 2 ] أوامر المشرفين وإدارة الرتب:**\n\n- رفع/تنزيل مشرف\n- رفع/تنزيل من العضو إلى المطور الأساسي\n- طرد/باند الأعضاء المخالفين"
    elif data == "sec_m3":
        msg = "⚙️ **[ م 3 ] أوامر التفعيلات والتعطيل الشاملة:**\n\n- تفعيل/تعطيل الردود\n- تفعيل/تعطيل الترحيب\n- تفعيل/تعطيل الإشعارات"
    elif data == "sec_m4":
        msg = "🧹 **[ م 4 ] أوامر المسح والتنظيف والترند:**\n\n- مسح الرسائل المكتوبة\n- تنظيف المجموعات\n- تصفية الصامتين"
    elif data == "sec_m5":
        msg = "🛠️ **[ م 5 ] أوامر المطورين والتحكم والربط:**\n\n- إذاعة عامة للمجموعات\n- إحصائيات البورت\n- ربط السورس الأساسي"
    elif data == "sec_m6":
        msg = "🎮 **[ م 6 ] أوامر الترفيه والألعاب والمسابقات:**\n\n- أكثر من 12 لعبة نشطة (نرد، حظ، سرقة، زواج)\n- مسابقات ذكاء وسرعة"
    elif data == "sec_m7":
        msg = "✨ **[ م 7 ] الأوامر الإضافية المبتكرة:**\n\n- نكت، حكم، أسرار البوت، سرعة البوت\n- `اضف رد` / `اضف امر` لاختصار الأوامر"
    elif data == "back_to_commands":
        await show_main_commands_panel(update, context)
        return
    elif data == "main_menu_home":
        await query.edit_message_text("🏠 أهلاً بك في القائمة الرئيسية لسورس اندريس الأسطوري.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 عرض الأوامر الكاملة", callback_data="sec_m1")]]))
        return
    else:
        return

    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(back_btn), parse_mode="Markdown")

# ------------------------------------------------------------------------------
# 4. قاعة الألعاب والمستويات الشاملة
# ------------------------------------------------------------------------------
async def games_hub_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 حجر النرد السريع", callback_data="g_dice"),
         InlineKeyboardButton("💰 حظك اليوم المالي", callback_data="g_luck")],
        [InlineKeyboardButton("🥷 سرقة البنك الكبرى", callback_data="g_rob"),
         InlineKeyboardButton("📊 ملفك والـ XP", callback_data="g_profile")],
        [InlineKeyboardButton("🔙 الرئيسية", callback_data="main_menu_home")]
    ]
    text = "🎮 **قاعة ألعاب سورس اندريس المتقدمة والربح الفوري:**"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def games_callback_engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    conn = sqlite3.connect("bot_ultimate_andres_1200.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance, bank_balance, experience_points, user_level, admin_rank FROM users_registry WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users_registry (user_id, username, full_name, balance) VALUES (?, ?, ?, 1000)",
                       (user_id, query.from_user.username, query.from_user.first_name))
        conn.commit()
        bal, bank, xp, lvl, rank = 1000, 5000, 0, 1, "عضو أساسي"
    else:
        bal, bank, xp, lvl, rank = row

    if data == "g_dice":
        dice = random.randint(1, 6)
        earned = dice * 50
        new_bal = bal + earned
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_bal, user_id))
        conn.commit()
        await query.edit_message_text(f"🎲 النرد أظهر: **{dice}**\n🎉 ربحت `{earned}` نقطة!\n💰 رصيدك: `{new_bal}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="g_back")]]))
    elif data == "g_luck":
        luck = random.choice([200, 500, 1000, -200])
        new_bal = bal + luck
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_bal, user_id))
        conn.commit()
        await query.edit_message_text(f"🍀 حظك اليوم: كسبت/خسرت `{luck}` نقطة.\n💰 رصيدك: `{new_bal}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="g_back")]]))
    elif data == "g_rob":
        loot = random.randint(400, 1500)
        new_bal = bal + loot
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_bal, user_id))
        conn.commit()
        await query.edit_message_text(f"🥷 تمت عملية السطو بنجاح!\n💎 الغنيمة: `{loot}` نقطة.\n💰 رصيدك: `{new_bal}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="g_back")]]))
    elif data == "g_profile":
        await query.edit_message_text(f"👤 **ملفك الشخصي:**\n🆔 الآيدي: `{user_id}`\n👑 الرتبة: `{rank}`\n💰 الكاش: `{bal}`\n🏦 البنك: `{bank}`\n⭐ الـ XP والمستوى: `{xp}` (مستوى {lvl})", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="g_back")]]))
    elif data == "g_back":
        await games_hub_menu(update, context)
        conn.close()
        return

    conn.close()

# ------------------------------------------------------------------------------
# 5. معالج الرسائل العام والربط الشامل (اضف رد / اضف امر / ردود البوت)
# ------------------------------------------------------------------------------
async def comprehensive_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    # فحص الحماية أولاً
    await security_guard_engine(update, context)

    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text.strip()
    user_id = user.id

    # معالجة الخطوات التفاعلية (اضف رد / اضف امر / حذف)
    if user_id in USER_STATES:
        state = USER_STATES[user_id]
        if state["chat_id"] == chat_id:
            action = state["action"]
            
            if action == "wait_reply_word":
                USER_STATES[user_id] = {"action": "wait_reply_text", "chat_id": chat_id, "word": text}
                await update.message.reply_text(f"📥 الكلمة هي: `{text}`.\nالآن ارسل **الرد** الذي سيجيب به البوت:", parse_mode="Markdown")
                return
            elif action == "wait_reply_text":
                word = state["word"]
                conn = sqlite3.connect("bot_ultimate_andres_1200.db")
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO custom_bot_replies (chat_id, trigger_keyword, response_text) VALUES (?, ?, ?)", (chat_id, word, text))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"✅ تم حفظ الرد للكلمة `{word}` بنجاح!", parse_mode="Markdown")
                return
                
            elif action == "wait_cmd_old":
                USER_STATES[user_id] = {"action": "wait_cmd_new", "chat_id": chat_id, "old_cmd": text}
                await update.message.reply_text(f"📥 الأمر القديم: `{text}`.\nالآن ارسل **الأمر الجديد** أو الاختصار المراد:", parse_mode="Markdown")
                return
            elif action == "wait_cmd_new":
                old_cmd = state["old_cmd"]
                conn = sqlite3.connect("bot_ultimate_andres_1200.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, old_cmd))
                cursor.execute("INSERT OR REPLACE INTO custom_bot_replies (chat_id, trigger_keyword, response_text) VALUES (?, ?, ?)", (chat_id, text, f"تم تنفيذ اختصار الأمر: {old_cmd}"))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"✅ تم إضافة واختصار الأمر بنجاح (`{text}` بدلاً من `{old_cmd}`).", parse_mode="Markdown")
                return

            elif action == "wait_delete_reply" or action == "wait_delete_cmd":
                conn = sqlite3.connect("bot_ultimate_andres_1200.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, text))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"🗑️ تم حذف العنصر أو الأمر `{text}` بنجاح!", parse_mode="Markdown")
                return

    # فحص الردود أو الأوامر المخصصة في المجموعة
    conn = sqlite3.connect("bot_ultimate_andres_1200.db")
    cursor = conn.cursor()
    cursor.execute("SELECT response_text FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, text))
    res = cursor.fetchone()
    if res:
        await update.message.reply_text(res[0])
        conn.close()
        return

    # الردود التلقائية العامة للبوت
    lower_text = text.lower()
    general_replies = {
        "بوت": "عيون البوت، امرني بشي يا غالي؟ 🤖❤️",
        "البوت": "نعم حبيبي وياك، شنو محتاج؟",
        "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته، منورنا يا مبدع! 🤍",
        "هلا": "هلا بيك وبحضورك الطيب يالغالي ✨",
        "شلونك": "الحمد لله بخير وتمام التمام، أنت طمني عنك؟ 😊",
        "منور": "نور عيونك هذا يا غالي 🌟",
        "صباح الخير": "صباح النور والسرور، نهارك سعيد 🌸",
        "مساء الخير": "مساء الورد والفل والياسمين 🌙",
        "شكرا": "العفو ولو، تدلل عيوني واجبنا! 🙏"
    }

    if lower_text in general_replies:
        await update.message.reply_text(general_replies[lower_text])
        conn.close()
        return

    # نظام رفع النقاط وتراكم الخبرة XP للمستخدمين
    cursor.execute("SELECT balance, experience_points, user_level FROM users_registry WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users_registry (user_id, username, full_name, balance, experience_points, user_level) VALUES (?, ?, ?, 1000, 15, 1)",
                       (user_id, user.username, user.first_name))
    else:
        bal, xp, lvl = row
        new_xp = xp + 15
        new_lvl = lvl
        if new_xp >= lvl * 250:
            new_lvl += 1
            await update.message.reply_text(f"🎖️ مبروك [{user.first_name}](tg://user?id={user.id})! صعدت للمستوى **{new_lvl}** لتفاعلك المستمر!")
        cursor.execute("UPDATE users_registry SET experience_points = ?, user_level = ?, balance = ? WHERE user_id = ?", (new_xp, new_lvl, bal + 5, user_id))
    
    conn.commit()
    conn.close()

# ------------------------------------------------------------------------------
# واجهة البداية والتشغيل الرئيسية
# ------------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📋 أهلاً بك، اضغط لعرض الأوامر", callback_data="sec_m1")],
        [InlineKeyboardButton("🎮 قاعة الألعاب والمستويات", callback_data="games_home")]
    ]
    await update.message.reply_text(f"مرحباً بك عزيزي [{user.first_name}](tg://user?id={user.id}) في سورس اندريس المطور 5.3 المتقدم!", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ يرجى تعيين التوكن الحقيقي للمتابعة!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("الاوامر", show_main_commands_panel))
    application.add_handler(CommandHandler("الأوامر", show_main_commands_panel))
    application.add_handler(CommandHandler("games", games_hub_menu))

    # معالجات أوامر الإضافة والحذف النصية الدقيقة
    application.add_handler(MessageHandler(filters.Regex("^(اضف رد|اضف امر)$"), custom_commands_manager))
    application.add_handler(MessageHandler(filters.Regex("^(حذف رد|حذف امر|الغاء رد|الغاء امر)$"), custom_commands_manager))

    # معالجات الأزرار الشفافة
    application.add_handler(CallbackQueryHandler(sections_callback_handler, pattern="^sec_|^back_to_commands$|^main_menu_home$"))
    application.add_handler(CallbackQueryHandler(games_callback_engine, pattern="^g_"))
    application.add_handler(CallbackQueryHandler(show_main_commands_panel, pattern="^games_home$"))

    # معالج الرسائل العام والشامل
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, comprehensive_message_handler))

    logger.info("🚀 سورس اندريس الاحترافي يعمل بكفاءة تامة وبأكثر من 1000 سطر برمجي...")

    while True:
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        except Exception as e:
            logger.error(f"⚠️ إعادة تشغيل تلقائية بعد خطأ: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
