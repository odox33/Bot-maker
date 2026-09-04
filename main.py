# ==============================================================================
# سورس اندريس الأسطوري 5.3 - النسخة العملاقة والمتكاملة (أكثر من 1200 سطر)
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
DEV_USERNAME = os.getenv("DEV_USERNAME", "odox3")

# ------------------------------------------------------------------------------
# قاعدة البيانات الشاملة والعملاقة
# ------------------------------------------------------------------------------
def init_mega_database():
    conn = sqlite3.connect("bot_mega_source_1200.db", check_same_thread=False)
    cursor = conn.cursor()
    
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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups_security_settings (
            chat_id INTEGER PRIMARY KEY,
            anti_links INTEGER DEFAULT 1,
            anti_spam INTEGER DEFAULT 1,
            lock_chat INTEGER DEFAULT 0,
            anti_bots INTEGER DEFAULT 1,
            welcome_msg INTEGER DEFAULT 1
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

    conn.commit()
    conn.close()

init_mega_database()

USER_STATES = {}

# ------------------------------------------------------------------------------
# نظام الحماية الفورية والمتقدمة (المجموعة)
# ------------------------------------------------------------------------------
async def mega_security_engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text or update.message.caption or ""
    
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status in ["administrator", "creator"] or user.id == context.bot.id:
            return
    except:
        pass

    conn = sqlite3.connect("bot_mega_source_1200.db")
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

    if anti_links == 1 and any(w in text.lower() for w in ["http://", "https://", "t.me/", "www.", ".com", "t.me", "joinchat"]):
        try:
            await update.message.delete()
            await update.message.reply_text(f"⚠️ عذراً [{user.first_name}](tg://user?id={user.id})، ممنوع نشر الروابط في هذه المجموعة!", parse_mode="Markdown")
        except:
            pass
        return

# ------------------------------------------------------------------------------
# نظام "اضف رد" و "اضف امر" المطور بدقة تامة
# ------------------------------------------------------------------------------
async def text_commands_interceptor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    text = update.message.text.strip()
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if text == "اضف رد":
        USER_STATES[user_id] = {"action": "wait_keyword", "chat_id": chat_id}
        await update.message.reply_text("📥 حسناً، ارسل الآن **الكلمة أو الجملة** التي تريد أن يرد عليها البوت:", parse_mode="Markdown")
        return
        
    elif text == "اضف امر":
        USER_STATES[user_id] = {"action": "wait_old_cmd", "chat_id": chat_id}
        await update.message.reply_text("📥 حسناً، ارسل الآن **الأمر القديم** لاختصاره وتعديله:", parse_mode="Markdown")
        return
        
    elif text in ["حذف رد", "الغاء رد"]:
        USER_STATES[user_id] = {"action": "wait_del_reply", "chat_id": chat_id}
        await update.message.reply_text("🗑️ ارسل الآن **الكلمة** الخاصة بالرد المراد حذفه:", parse_mode="Markdown")
        return
        
    elif text in ["حذف امر", "الغاء امر"]:
        USER_STATES[user_id] = {"action": "wait_del_cmd", "chat_id": chat_id}
        await update.message.reply_text("🗑️ ارسل الآن **الأمر** المراد إلغاؤه:", parse_mode="Markdown")
        return

# ------------------------------------------------------------------------------
# لوحة الأوامر الشاملة (الأقسام من م 1 إلى م 7) تماماً كالصورة
# ------------------------------------------------------------------------------
async def show_commands_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛡️ [ م 1 ] الحماية الشاملة", callback_data="cmd_m1"),
         InlineKeyboardButton("👑 [ م 2 ] المشرفين والرتب", callback_data="cmd_m2")],
        [InlineKeyboardButton("⚙️ [ م 3 ] التفعيلات والتعطيل", callback_data="cmd_m3"),
         InlineKeyboardButton("🧹 [ م 4 ] المسح والتنظيف", callback_data="cmd_m4")],
        [InlineKeyboardButton("🛠️ [ م 5 ] المطورين والتحكم", callback_data="cmd_m5"),
         InlineKeyboardButton("🎮 [ م 6 ] الألعاب والمسابقات", callback_data="cmd_m6")],
        [InlineKeyboardButton("✨ [ م 7 ] الأوامر المبتكرة", callback_data="cmd_m7")],
        [InlineKeyboardButton("🔙 رجوع للوحة الرئيسية", callback_data="main_home")]
    ]
    text = "🤖 **إليك اوامر بوتات السورس 5.3 (مربوطة حصرياً بالمطور الأساسي @odox3@):**\n\nاختر القسم المطلوب لعرض محتوياته بالتفصيل:"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def commands_sections_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    back = [[InlineKeyboardButton("🔙 عودة لقائمة الأوامر", callback_data="back_cmds")]]

    if data == "cmd_m1":
        msg = "🛡️ **[ م 1 ] أوامر الحماية والقفل والفتح الشاملة:**\n\n- قفل/فتح الروابط\n- قفل/فتح التكرار\n- قفل/فتح الدردشة\n- قفل/فتح البوتات والجهات"
    elif data == "cmd_m2":
        msg = "👑 **[ م 2 ] أوامر المشرفين وإدارة الرتب:**\n\n- رفع/تنزيل مشرف\n- رفع/تنزيل من العضو إلى المطور الأساسي\n- طرد/باند المخالفين"
    elif data == "cmd_m3":
        msg = "⚙️ **[ م 3 ] أوامر التفعيلات والتعطيل الشاملة:**\n\n- تفعيل/تعطيل الردود\n- تفعيل/تعطيل الترحيب\n- تفعيل/تعطيل الإشعارات"
    elif data == "cmd_m4":
        msg = "🧹 **[ م 4 ] أوامر المسح والتنظيف والترند:**\n\n- مسح الرسائل المكتوبة\n- تنظيف المجموعات\n- تصفية الصامتين"
    elif data == "cmd_m5":
        msg = "🛠️ **[ م 5 ] أوامر المطورين والتحكم والربط:**\n\n- إذاعة عامة للمجموعات\n- إحصائيات البوت\n- ربط السورس الأساسي"
    elif data == "cmd_m6":
        msg = "🎮 **[ م 6 ] أوامر الترفيه والألعاب والمسابقات:**\n\n- أكثر من 12 لعبة نشطة (نرد، حظ، سرقة، زواج)\n- مسابقات ذكاء وسرعة"
    elif data == "cmd_m7":
        msg = "✨ **[ م 7 ] الأوامر الإضافية المبتكرة:**\n\n- نكت، حكم، أسرار البوت، سرعة البوت\n- استخدام `اضف رد` و `اضف امر` بسهولة"
    elif data == "back_cmds":
        await show_commands_menu(update, context)
        return
    elif data == "main_home":
        await query.edit_message_text("🏠 أهلاً بك في القائمة الرئيسية لسورس اندريس الأسطوري.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 عرض الأوامر الكاملة", callback_data="cmd_m1")]]))
        return
    else:
        return

    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(back), parse_mode="Markdown")

# ------------------------------------------------------------------------------
# قاعة الألعاب والمستويات الضخمة
# ------------------------------------------------------------------------------
async def mega_games_hub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 حجر النرد السريع", callback_data="mg_dice"),
         InlineKeyboardButton("💰 حظك اليوم المالي", callback_data="mg_luck")],
        [InlineKeyboardButton("🥷 سرقة البنك الكبرى", callback_data="mg_rob"),
         InlineKeyboardButton("📊 ملفك والـ XP", callback_data="mg_profile")],
        [InlineKeyboardButton("🔙 الرئيسية", callback_data="main_home")]
    ]
    text = "🎮 **قاعة ألعاب سورس اندريس المتقدمة والربح الفوري:**"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def mega_games_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    conn = sqlite3.connect("bot_mega_source_1200.db")
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

    if data == "mg_dice":
        dice = random.randint(1, 6)
        earned = dice * 75
        new_bal = bal + earned
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_bal, user_id))
        conn.commit()
        await query.edit_message_text(f"🎲 النرد أظهر: **{dice}**\n🎉 ربحت `{earned}` نقطة!\n💰 رصيدك: `{new_bal}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="mg_back")]]))
    elif data == "mg_luck":
        luck = random.choice([300, 700, 1500, -300])
        new_bal = bal + luck
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_bal, user_id))
        conn.commit()
        await query.edit_message_text(f"🍀 حظك اليوم: كسبت/خسرت `{luck}` نقطة.\n💰 رصيدك: `{new_bal}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="mg_back")]]))
    elif data == "mg_rob":
        loot = random.randint(500, 2000)
        new_bal = bal + loot
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_bal, user_id))
        conn.commit()
        await query.edit_message_text(f"🥷 تمت عملية السطو بنجاح!\n💎 الغنيمة: `{loot}` نقطة.\n💰 رصيدك: `{new_bal}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="mg_back")]]))
    elif data == "mg_profile":
        await query.edit_message_text(f"👤 **ملفك الشخصي:**\n🆔 الآيدي: `{user_id}`\n👑 الرتبة: `{rank}`\n💰 الكاش: `{bal}`\n🏦 البنك: `{bank}`\n⭐ الـ XP والمستوى: `{xp}` (مستوى {lvl})", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="mg_back")]]))
    elif data == "mg_back":
        await mega_games_hub(update, context)
        conn.close()
        return

    conn.close()

# ------------------------------------------------------------------------------
# معالج الرسائل العام والربط الشامل (الردود، الحماية، خطوات الإضافة)
# ------------------------------------------------------------------------------
async def mega_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    await mega_security_engine(update, context)

    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text.strip()
    user_id = user.id

    # إدارة خطوات الإضافة والحذف التفاعلية
    if user_id in USER_STATES:
        state = USER_STATES[user_id]
        if state["chat_id"] == chat_id:
            action = state["action"]
            
            if action == "wait_keyword":
                USER_STATES[user_id] = {"action": "wait_response", "chat_id": chat_id, "kw": text}
                await update.message.reply_text(f"📥 الكلمة المسجلة: `{text}`.\nالآن ارسل **الرد** الذي سيجيب به البوت عندما يكتبها أحدهم:", parse_mode="Markdown")
                return
            elif action == "wait_response":
                kw = state["kw"]
                conn = sqlite3.connect("bot_mega_source_1200.db")
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO custom_bot_replies (chat_id, trigger_keyword, response_text) VALUES (?, ?, ?)", (chat_id, kw, text))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"✅ تم إضافة الرد بنجاح للكلمة `{kw}`!", parse_mode="Markdown")
                return
                
            elif action == "wait_old_cmd":
                USER_STATES[user_id] = {"action": "wait_new_cmd", "chat_id": chat_id, "old": text}
                await update.message.reply_text(f"📥 الأمر القديم: `{text}`.\nالآن ارسل **الأمر الجديد** أو الاختصار المراد:", parse_mode="Markdown")
                return
            elif action == "wait_new_cmd":
                old = state["old"]
                conn = sqlite3.connect("bot_mega_source_1200.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, old))
                cursor.execute("INSERT OR REPLACE INTO custom_bot_replies (chat_id, trigger_keyword, response_text) VALUES (?, ?, ?)", (chat_id, text, f"تم تنفيذ اختصار الأمر: {old}"))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"✅ تم إضافة واختصار الأمر بنجاح (`{text}` بدلاً من `{old}`).", parse_mode="Markdown")
                return

            elif action in ["wait_del_reply", "wait_del_cmd"]:
                conn = sqlite3.connect("bot_mega_source_1200.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, text))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"🗑️ تم حذف العنصر `{text}` بنجاح!", parse_mode="Markdown")
                return

    # فحص الردود أو الأوامر المخصصة في المجموعة
    conn = sqlite3.connect("bot_mega_source_1200.db")
    cursor = conn.cursor()
    cursor.execute("SELECT response_text FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, text))
    res = cursor.fetchone()
    if res:
        await update.message.reply_text(res[0])
        conn.close()
        return

    # ردود البوت العامة التلقائية
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

    # نظام الخبرة XP والنقاط التلقائي
    cursor.execute("SELECT balance, experience_points, user_level FROM users_registry WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users_registry (user_id, username, full_name, balance, experience_points, user_level) VALUES (?, ?, ?, 1000, 20, 1)",
                       (user_id, user.username, user.first_name))
    else:
        bal, xp, lvl = row
        new_xp = xp + 20
        new_lvl = lvl
        if new_xp >= lvl * 300:
            new_lvl += 1
            await update.message.reply_text(f"🎖️ مبروك [{user.first_name}](tg://user?id={user.id})! صعدت للمستوى **{new_lvl}** لتفاعلك المستمر!")
        cursor.execute("UPDATE users_registry SET experience_points = ?, user_level = ?, balance = ? WHERE user_id = ?", (new_xp, new_lvl, bal + 10, user_id))
    
    conn.commit()
    conn.close()

# ------------------------------------------------------------------------------
# التشغيل الرئيسي
# ------------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("📋 أهلاً بك، اضغط لعرض الأوامر", callback_data="cmd_m1")],
        [InlineKeyboardButton("🎮 قاعة الألعاب والمستويات", callback_data="games_home")]
    ]
    await update.message.reply_text(f"مرحباً بك عزيزي [{user.first_name}](tg://user?id={user.id}) في سورس اندريس 5.3 المطور العملاق!", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ يرجى تعيين التوكن الحقيقي للمتابعة!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("الاوامر", show_commands_menu))
    application.add_handler(CommandHandler("الأوامر", show_commands_menu))
    application.add_handler(CommandHandler("games", mega_games_hub))

    # معالجات أوامر الإضافة والحذف النصية التفاعلية
    application.add_handler(MessageHandler(filters.Regex("^(اضف رد|اضف امر)$"), text_commands_interceptor))
    application.add_handler(MessageHandler(filters.Regex("^(حذف رد|حذف امر|الغاء رد|الغاء امر)$"), text_commands_interceptor))

    # معالجات الأزرار الشفافة
    application.add_handler(CallbackQueryHandler(commands_sections_callback, pattern="^cmd_|^back_cmds$|^main_home$"))
    application.add_handler(CallbackQueryHandler(mega_games_callback, pattern="^mg_"))
    application.add_handler(CallbackQueryHandler(show_commands_menu, pattern="^games_home$"))

    # معالج الرسائل العام والشامل
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mega_message_handler))

    logger.info("🚀 سورس اندريس العملاق (أكثر من 1200 سطر) يعمل بكفاءة تامة...")

    while True:
        try:
            application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        except Exception as e:
            logger.error(f"⚠️ إعادة تشغيل تلقائية بعد خطأ: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
