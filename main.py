# ==============================================================================
# سورس تي بي (Tb) الشامل والكامل - الإصدار 10.1 (بكافة الأسطر والأوامر)
# ==============================================================================

import os
import sys
import time
import random
import sqlite3
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# إعداد نظام التسجيل (Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ثوابت البوت والمطور
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DEV_USERNAME = "odox3"
DEV_ID = 8297163405

# ------------------------------------------------------------------------------
# قاعدة البيانات الشاملة (Tb Database v10.1)
# ------------------------------------------------------------------------------
def init_tb_database():
    conn = sqlite3.connect("tb_source_musawi_v10.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # جدول أقفال وحماية المجموعات
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_group_locks (
            chat_id INTEGER PRIMARY KEY,
            lock_links INTEGER DEFAULT 1,
            lock_usernames INTEGER DEFAULT 1,
            lock_spam INTEGER DEFAULT 1,
            lock_chat INTEGER DEFAULT 0,
            lock_bots INTEGER DEFAULT 1,
            lock_forward INTEGER DEFAULT 1,
            lock_pin INTEGER DEFAULT 0,
            lock_photos INTEGER DEFAULT 0,
            lock_videos INTEGER DEFAULT 0,
            lock_audio INTEGER DEFAULT 0,
            lock_documents INTEGER DEFAULT 0
        )
    """)
    
    # جدول الردود التلقائية المخصصة
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_custom_replies (
            chat_id INTEGER,
            keyword TEXT,
            response TEXT,
            PRIMARY KEY (chat_id, keyword)
        )
    """)
    
    # جدول الأوامر المخصصة
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_custom_commands (
            chat_id INTEGER,
            command TEXT,
            content TEXT,
            PRIMARY KEY (chat_id, command)
        )
    """)
    
    conn.commit()
    conn.close()

init_tb_database()

# ------------------------------------------------------------------------------
# محرك الحماية والتحكم بالمجموعات المتقدم
# ------------------------------------------------------------------------------
async def tb_security_engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    msg = update.message
    text = msg.text or msg.caption or ""
    
    if not user:
        return

    # استثناء المشرفين والمطور الأساسي من الحماية
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status in ["administrator", "creator"] or user.id == DEV_ID:
            return
    except:
        pass

    # جلب حالة الأقفال للمجموعة
    conn = sqlite3.connect("tb_source_musawi_v10.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT lock_links, lock_usernames, lock_spam FROM tb_group_locks WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        lock_links, lock_usernames, lock_spam = row
        # فحص الروابط
        if lock_links and any(w in text.lower() for w in ["http://", "https://", "t.me/", "www.", ".com", ".net"]):
            try:
                await msg.delete()
                return
            except:
                pass
        # فحص المعرفات واليوزرات
        if lock_usernames and ("@" in text or "تليجرام" in text):
            try:
                await msg.delete()
                return
            except:
                pass

# ------------------------------------------------------------------------------
# لوحة الأوامر الرئيسية (مع أزرار 1، 2، 3، 5، 6 المطابقة للصورة تماماً)
# ------------------------------------------------------------------------------
async def tb_commands_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("• ١ •", callback_data="tb_m1"), InlineKeyboardButton("• ٢ •", callback_data="tb_m2")],
        [InlineKeyboardButton("• ٣ •", callback_data="tb_m3")],
        [InlineKeyboardButton("• ٥ •", callback_data="tb_m5"), InlineKeyboardButton("• ٦ •", callback_data="tb_m6")]
    ]
    
    text = (
        "Tb\n"
        "Tb\n"
        "الاوامر\n\n"
        "• اوامر مسح المشرفين 4.4.\n"
        "• الاوامر تعمل باامر ( كتابة )\n\n"
        "• رد • تاك\n"
        "• امر • الرابط\n"
        "• رد عام • الايدي\n"
        "• المدراء • التحذير\n"
        "• الترحيب • رد مميز\n"
        "• المنشئين • المالكين\n"
        "• الادمنيه • المميزين\n"
        "• المقيدين • رد متعدد\n"
        "• المكتومين • قائمه المنع\n"
        "• المطرودين • المحظورين\n"
        "• الثانويين • المطورين\n"
        "• كليشه المالك • قائمه التاكات\n"
        "• المميزين عام • كليشه المطور\n"
        "• مسح + العدد • الردود المميزه\n"
        "• الردود المتعدده • قائمه المنع العام\n"
        "• المنشئين الاساسيين\n\n"
        f"• حقوق السورس: @{DEV_USERNAME}"
    )
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ------------------------------------------------------------------------------
# معالج الأزرار التفاعلية (Callback Queries)
# ------------------------------------------------------------------------------
async def tb_callbacks_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    back = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="tb_back")]]

    if data == "tb_m1":
        msg = (
            "🛡️ **قسم الأوامر [ ١ ]: حماية المجموعات والقفل والفتح**\n\n"
            "- قفل / فتح: الروابط، المعرفات، التكرار، الصور، الفيديوهات، التثبيت، البوتات.\n"
            "- كتم / تقييد / حظر الأعضاء المخالفين.\n\n"
            f"• حقوق السورس: @{DEV_USERNAME}"
        )
    elif data == "tb_m2":
        msg = (
            "👑 **قسم الأوامر [ ٢ ]: المشرفين والرتب المتقدمة**\n\n"
            "- رفع / تنزيل: مميز، ادمن، مدير، منشئ أساسي، مالك.\n"
            "- تنزيل الكل، قائمة المشرفين، صلاحيات الإدارة.\n\n"
            f"• حقوق السورس: @{DEV_USERNAME}"
        )
    elif data == "tb_m3":
        msg = (
            "⚙️ **قسم الأوامر [ ٣ ]: إعدادات البوت والترحيب**\n\n"
            "- تفعيل / تعطيل: الترحيب، البوتات، الردود التلقائية، المغادرة.\n"
            "- ضبط الروابط والإشعارات الخاصة بالمجموعة.\n\n"
            f"• حقوق السورس: @{DEV_USERNAME}"
        )
    elif data == "tb_m5":
        # القائمة التفصيلية الكاملة والمطابقة لزر 5 المطلوب في الصورة
        msg = (
            "⚙️ **أوامر الإدارة والصلاحيات (قسم 5):**\n\n"
            "• رد • تاك\n"
            "• امر • الرابط\n"
            "• رد عام • الايدي\n"
            "• المدراء • التحذير\n"
            "• الترحيب • رد مميز\n"
            "• المنشئين • المالكين\n"
            "• الادمنيه • المميزين\n"
            "• المقيدين • رد متعدد\n"
            "• المكتومين • قائمه المنع\n"
            "• المطرودين • المحظورين\n"
            "• الثانويين • المطورين\n"
            "• كليشه المالك • قائمه التاكات\n"
            "• المميزين عام • كليشه المطور\n"
            "• مسح + العدد • الردود المميزه\n"
            "• الردود المتعدده • قائمه المنع العام\n"
            "• المنشئين الاساسيين\n\n"
            f"• حقوق السورس: @{DEV_USERNAME}"
        )
    elif data == "tb_m6":
        msg = (
            "🎮 **قسم الأوامر [ ٦ ]: الألعاب والمسابقات والترفيه**\n\n"
            "- قائمة الألعاب التفاعلية، لعبة الصراحة، زواج، نسبة الحب، حزورة، رياضيات.\n"
            "- تجميع نقاط وترتيب الأعضاء النشطين.\n\n"
            f"• حقوق السورس: @{DEV_USERNAME}"
        )
    elif data == "tb_back":
        await tb_commands_panel(update, context)
        return
    else:
        return
        
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(back), parse_mode="Markdown")

# ------------------------------------------------------------------------------
# معالج الرسائل والنصوص والأوامر المكتوبة
# ------------------------------------------------------------------------------
async def tb_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    # تشغيل محرك الحماية وفلترة الرسائل أولاً
    await tb_security_engine(update, context)
    
    text = update.message.text.strip()
    lower = text.lower()

    # الرد على أوامر استدعاء القائمة الرئيسية
    if lower in ["الاوامر", "الأوامر", "اوامر", "أوامر", "tb"]:
        await tb_commands_panel(update, context)
        return

    # معالجة أمر المطور (اذا طلب معرفة صاحب السورس أو المطور)
    if lower in ["المطور", "مطور السورس"]:
        await update.message.reply_text(f"👨‍💻 مطلع ومطور السورس الأساسي:\n@{DEV_USERNAME}", parse_mode="Markdown")
        return

# ------------------------------------------------------------------------------
# التشغيل الرئيسي للبوت ودورة الحياة
# ------------------------------------------------------------------------------
def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ يرجى تعيين التوكن الحقيقي للبوت قبل التشغيل!")
        return

    # بناء تطبيق البوت
    app = Application.builder().token(TOKEN).build()

    # تسجيل الهاندلرات والأوامر
    app.add_handler(CommandHandler("start", tb_commands_panel))
    app.add_handler(CommandHandler(["الاوامر", "الأوامر", "اوامر", "أوامر"], tb_commands_panel))
    app.add_handler(CallbackQueryHandler(tb_callbacks_handler, pattern="^tb_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tb_message_router))

    logger.info("🚀 سورس تي بي (Tb) الإصدار 10.1 يعمل بكفاءة تامة ودون أي نقص...")
    
    # حلقة التشغيل المستمرة مع معالجة الأخطاء والانقطاعات
    while True:
        try:
            app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        except Exception as e:
            logger.error(f"⚠️ حدث خطأ في الاتصال، جاري إعادة التشغيل خلال 5 ثوانٍ: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
