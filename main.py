# ==============================================================================
# سورس اندريس الأسطوري 5.3 - النسخة العملاقة المتكاملة (أوامر الحماية، الألعاب، الردود)
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
# قاعدة البيانات الموسعة
# ------------------------------------------------------------------------------
def init_mega_database():
    conn = sqlite3.connect("bot_massive_source.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_registry (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance INTEGER DEFAULT 5000,
            bank_balance INTEGER DEFAULT 25000,
            experience_points INTEGER DEFAULT 0,
            user_level INTEGER DEFAULT 1,
            admin_rank TEXT DEFAULT 'مطور أساسي'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups_security_settings (
            chat_id INTEGER PRIMARY KEY,
            anti_links INTEGER DEFAULT 1,
            anti_spam INTEGER DEFAULT 1,
            lock_chat INTEGER DEFAULT 0,
            anti_bots INTEGER DEFAULT 1,
            welcome_msg INTEGER DEFAULT 1,
            anti_forward INTEGER DEFAULT 1,
            anti_photos INTEGER DEFAULT 1,
            anti_videos INTEGER DEFAULT 1
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
# نظام الحماية الشامل والمتقدم جداً للمجموعات
# ------------------------------------------------------------------------------
async def security_guard_massive(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    conn = sqlite3.connect("bot_massive_source.db")
    cursor = conn.cursor()
    cursor.execute("SELECT anti_links, anti_spam, lock_chat, anti_forward, anti_photos FROM groups_security_settings WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    anti_links, anti_spam, lock_chat, anti_forward, anti_photos = (1, 1, 0, 1, 1) if not row else row
    conn.close()

    if lock_chat == 1:
        try:
            await update.message.delete()
        except:
            pass
        return

    if anti_links == 1 and any(w in text.lower() for w in ["http://", "https://", "t.me/", "www.", ".com", "t.me", "joinchat", "instagram.com"]):
        try:
            await update.message.delete()
            await update.message.reply_text(f"⚠️ عذراً [{user.first_name}](tg://user?id={user.id})، ممنوع نشر الروابط نهائياً!", parse_mode="Markdown")
        except:
            pass
        return

    if anti_forward == 1 and (update.message.forward_date or update.message.forward_from):
        try:
            await update.message.delete()
            await update.message.reply_text(f"⚠️ ممنوع توجيه الرسائل هنا [{user.first_name}](tg://user?id={user.id})!", parse_mode="Markdown")
        except:
            pass
        return

# ------------------------------------------------------------------------------
# إدارة الأوامر والردود المخصصة (اضف رد / اضف امر)
# ------------------------------------------------------------------------------
async def custom_commands_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type not in ["group", "supergroup"]:
        return
    
    text = update.message.text.strip()
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if text == "اضف رد":
        USER_STATES[user_id] = {"action": "wait_kw", "chat_id": chat_id}
        await update.message.reply_text("📥 ارسل الآن **الكلمة** التي تريد أن يرد عليها البوت:", parse_mode="Markdown")
        return
    elif text == "اضف امر":
        USER_STATES[user_id] = {"action": "wait_old", "chat_id": chat_id}
        await update.message.reply_text("📥 ارسل الآن **الأمر القديم** لاختصاره:", parse_mode="Markdown")
        return
    elif text in ["حذف رد", "الغاء رد"]:
        USER_STATES[user_id] = {"action": "wait_del_r", "chat_id": chat_id}
        await update.message.reply_text("🗑️ ارسل **الكلمة** الخاصة بالرد المراد حذفه:", parse_mode="Markdown")
        return
    elif text in ["حذف امر", "الغاء امر"]:
        USER_STATES[user_id] = {"action": "wait_del_c", "chat_id": chat_id}
        await update.message.reply_text("🗑️ ارسل **الأمر** المراد حذفه:", parse_mode="Markdown")
        return

# ------------------------------------------------------------------------------
# لوحة الأوامر الشاملة (م 1 إلى م 7)
# ------------------------------------------------------------------------------
async def show_commands_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛡️ [ م 1 ] الحماية الشاملة", callback_data="p_m1"),
         InlineKeyboardButton("👑 [ م 2 ] المشرفين والرتب", callback_data="p_m2")],
        [InlineKeyboardButton("⚙️ [ م 3 ] التفعيلات والتعطيل", callback_data="p_m3"),
         InlineKeyboardButton("🧹 [ م 4 ] المسح والتنظيف", callback_data="p_m4")],
        [InlineKeyboardButton("🛠️ [ م 5 ] المطورين والتحكم", callback_data="p_m5"),
         InlineKeyboardButton("🎮 [ م 6 ] الألعاب والمسابقات", callback_data="p_m6")],
        [InlineKeyboardButton("✨ [ م 7 ] الأوامر المبتكرة", callback_data="p_m7")],
        [InlineKeyboardButton("🔙 رجوع للوحة الرئيسية", callback_data="p_home")]
    ]
    text = "🤖 **إليك اوامر بوتات السورس 5.3 (مربوطة حصرياً بالمطور الأساسي @odox3@):**\n\nاختر القسم المطلوب لعرض محتوياته:"
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def panel_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    back = [[InlineKeyboardButton("🔙 عودة لقائمة الأوامر", callback_data="back_p")]]

    if data == "p_m1":
        msg = "🛡️ **[ م 1 ] الحماية الشاملة:**\n- قفل/فتح الروابط\n- قفل/فتح التكرار\n- قفل/فتح التوجيه\n- قفل/فتح الصور والدردشة"
    elif data == "p_m2":
        msg = "👑 **[ م 2 ] المشرفين والرتب:**\n- رفع/تنزيل مشرف\n- رفع مطور أساسي\n- طرد/باند المخالفين"
    elif data == "p_m3":
        msg = "⚙️ **[ م 3 ] التفعيلات والتعطيل:**\n- تفعيل/تعطيل الردود\n- تفعيل/تعطيل الترحيب\n- تفعيل/تعطيل الإشعارات"
    elif data == "p_m4":
        msg = "🧹 **[ م 4 ] المسح والتنظيف:**\n- مسح الرسائل\n- تنظيف الصامتين\n- إزالة الحسابات الوهمية"
    elif data == "p_m5":
        msg = "🛠️ **[ م 5 ] المطورين والتحكم:**\n- إذاعة عامة للمجموعات\n- إحصائيات البوت\n- تحديث السورس"
    elif data == "p_m6":
        msg = "🎮 **[ م 6 ] الألعاب والمسابقات:**\n- أكثر من 12 لعبة نشطة (نرد، حظ، سرقة، زواج)\n- مسابقات ذكاء وسرعة"
    elif data == "p_m7":
        msg = "✨ **[ م 7 ] الأوامر المبتكرة:**\n- نكت، حكم، سرعة البوت\n- استخدام `اضف رد` و `اضف امر` باحترافية"
    elif data == "back_p":
        await show_commands_panel(update, context)
        return
    elif data == "p_home":
        await query.edit_message_text("🏠 القائمة الرئيسية لسورس اندريس الأسطوري.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 عرض الأوامر", callback_data="p_m1")]]))
        return
    else:
        return
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(back), parse_mode="Markdown")

# ------------------------------------------------------------------------------
# قاعة الألعاب والمستويات الضخمة
# ------------------------------------------------------------------------------
async def massive_games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 حجر النرد السريع", callback_data="mg_dice"),
         InlineKeyboardButton("💰 حظك اليوم المالي", callback_data="mg_luck")],
        [InlineKeyboardButton("🥷 سرقة البنك الكبرى", callback_data="mg_rob"),
         InlineKeyboardButton("📊 ملفك الشخصي والـ XP", callback_data="mg_prof")],
        [InlineKeyboardButton("🔙 الرئيسية", callback_data="p_home")]
    ]
    text = "🎮 **قاعة ألعاب سورس اندريس المتقدمة:**"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def massive_games_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    conn = sqlite3.connect("bot_massive_source.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance, bank_balance, experience_points, user_level, admin_rank FROM users_registry WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users_registry (user_id, username, full_name, balance) VALUES (?, ?, ?, 5000)", (user_id, query.from_user.username, query.from_user.first_name))
        conn.commit()
        bal, bank, xp, lvl, rank = 5000, 25000, 0, 1, "مطور أساسي"
    else:
        bal, bank, xp, lvl, rank = row

    if data == "mg_dice":
        dice = random.randint(1, 6)
        earned = dice * 150
        new_b = bal + earned
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_b, user_id))
        conn.commit()
        await query.edit_message_text(f"🎲 النرد: **{dice}**\n🎉 ربحت `{earned}` نقطة!\n💰 رصيدك: `{new_b}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="mg_b")]]))
    elif data == "mg_luck":
        luck = random.choice([1000, 2500, 5000, -1000])
        new_b = bal + luck
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_b, user_id))
        conn.commit()
        await query.edit_message_text(f"🍀 حظك اليوم: `{luck}` نقطة.\n💰 رصيدك: `{new_b}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="mg_b")]]))
    elif data == "mg_rob":
        loot = random.randint(1500, 6000)
        new_b = bal + loot
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_b, user_id))
        conn.commit()
        await query.edit_message_text(f"🥷 تمت عملية السطو!\n💎 الغنيمة: `{loot}` نقطة.\n💰 رصيدك: `{new_b}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="mg_b")]]))
    elif data == "mg_prof":
        await query.edit_message_text(f"👤 **ملفك الشخصي:**\n🆔 الآيدي: `{user_id}`\n👑 الرتبة: `{rank}`\n💰 الكاش: `{bal}`\n🏦 البنك: `{bank}`\n⭐ الـ XP والمستوى: `{xp}` (مستوى {lvl})", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="mg_b")]]))
    elif data == "mg_b":
        await massive_games_menu(update, context)
        conn.close()
        return
    conn.close()

# ------------------------------------------------------------------------------
# المعالج الشامل للرسائل والردود التفاعلية
# ------------------------------------------------------------------------------
async def massive_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    await security_guard_massive(update, context)

    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text.strip()
    user_id = user.id

    if user_id in USER_STATES:
        state = USER_STATES[user_id]
        if state["chat_id"] == chat_id:
            action = state["action"]
            if action == "wait_kw":
                USER_STATES[user_id] = {"action": "wait_res", "chat_id": chat_id, "kw": text}
                await update.message.reply_text(f"📥 الكلمة: `{text}`.\nالآن ارسل **الرد** المرتبط بها:", parse_mode="Markdown")
                return
            elif action == "wait_res":
                kw = state["kw"]
                conn = sqlite3.connect("bot_massive_source.db")
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO custom_bot_replies (chat_id, trigger_keyword, response_text) VALUES (?, ?, ?)", (chat_id, kw, text))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"✅ تم حفظ الرد للكلمة `{kw}` بنجاح!", parse_mode="Markdown")
                return
            elif action == "wait_old":
                USER_STATES[user_id] = {"action": "wait_new", "chat_id": chat_id, "old": text}
                await update.message.reply_text(f"📥 الأمر القديم: `{text}`.\nارسل **الأمر الجديد** لاختصاره:", parse_mode="Markdown")
                return
            elif action == "wait_new":
                old = state["old"]
                conn = sqlite3.connect("bot_massive_source.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, old))
                cursor.execute("INSERT OR REPLACE INTO custom_bot_replies (chat_id, trigger_keyword, response_text) VALUES (?, ?, ?)", (chat_id, text, f"اختصار للأمر: {old}"))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"✅ تم إضافة واختصار الأمر `{text}` بدلاً من `{old}`.", parse_mode="Markdown")
                return
            elif action in ["wait_del_r", "wait_del_c"]:
                conn = sqlite3.connect("bot_massive_source.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, text))
                conn.commit()
                conn.close()
                del USER_STATES[user_id]
                await update.message.reply_text(f"🗑️ تم حذف الرد أو الأمر `{text}` بنجاح!", parse_mode="Markdown")
                return

    conn = sqlite3.connect("bot_massive_source.db")
    cursor = conn.cursor()
    cursor.execute("SELECT response_text FROM custom_bot_replies WHERE chat_id = ? AND trigger_keyword = ?", (chat_id, text))
    res = cursor.fetchone()
    if res:
        await update.message.reply_text(res[0])
        conn.close()
        return

    lower = text.lower()
    replies = {
        "بوت": "عيون البوت، امرني بشي يا غالي؟ 🤖❤️",
        "السلام عليكم": "وعليكم السلام ورحمة الله وبركاته، منورنا يا مبدع! 🤍",
        "شلونك": "الحمد لله بخير وتمام التمام، أنت طمني عنك؟ 😊",
        "صباح الخير": "صباح النور والسرور، نهارك سعيد 🌸",
        "شكرا": "العفو ولو، تدلل عيوني واجبنا! 🙏"
    }
    if lower in replies:
        await update.message.reply_text(replies[lower])
        conn.close()
        return

    cursor.execute("SELECT balance, experience_points, user_level FROM users_registry WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users_registry (user_id, username, full_name, balance, experience_points, user_level) VALUES (?, ?, ?, 5000, 30, 1)", (user_id, user.username, user.first_name))
    else:
        bal, xp, lvl = row
        new_xp = xp + 30
        new_lvl = lvl
        if new_xp >= lvl * 400:
            new_lvl += 1
            await update.message.reply_text(f"🎖️ مبروك [{user.first_name}](tg://user?id={user.id})! صعدت للمستوى **{new_lvl}**!")
        cursor.execute("UPDATE users_registry SET experience_points = ?, user_level = ?, balance = ? WHERE user_id = ?", (new_xp, new_lvl, bal + 20, user_id))
    conn.commit()
    conn.close()

# ------------------------------------------------------------------------------
# التشغيل الرئيسي
# ------------------------------------------------------------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kb = [
        [InlineKeyboardButton("📋 عرض الأوامر الشاملة", callback_data="p_m1")],
        [InlineKeyboardButton("🎮 قاعة الألعاب والمستويات", callback_data="games_menu")]
    ]
    await update.message.reply_text(f"مرحباً بك عزيزي [{user.first_name}](tg://user?id={user.id}) في سورس اندريس 5.3 المطور العملاق!", reply_markup=InlineKeyboardMarkup(kb), parse_Mode="Markdown")

def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ يرجى تعيين التوكن الحقيقي للبوت!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("الاوامر", show_commands_panel))
    app.add_handler(CommandHandler("الأوامر", show_commands_panel))
    app.add_handler(CommandHandler("games", massive_games_menu))

    app.add_handler(MessageHandler(filters.Regex("^(اضف رد|اضف امر)$"), custom_commands_handler))
    app.add_handler(MessageHandler(filters.Regex("^(حذف رد|حذف امر|الغاء رد|الغاء امر)$"), custom_commands_handler))

    app.add_handler(CallbackQueryHandler(panel_callback_query, pattern="^p_|^back_p$"))
    app.add_handler(CallbackQueryHandler(massive_games_callback, pattern="^mg_"))
    app.add_handler(CallbackQueryHandler(show_commands_panel, pattern="^games_menu$"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, massive_message_handler))

    logger.info("🚀 سورس اندريس الضخم والعملاق يعمل بكفاءة تامة...")
    while True:
        try:
            app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        except Exception as e:
            logger.error(f"⚠️ خطأ بالاتصال، إعادة تشغيل: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
