# ==============================================================================
# سورس تي بي (Tb) الأسطوري المطور - النسخة العملاقة والمتكاملة 7.0 (2026)
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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DEV_USERNAME = "odox3"
DEV_ID = 8297163405

# ------------------------------------------------------------------------------
# قاعدة البيانات الشاملة لإدارة المجموعات، الحماية، السيرفرات، والأعضاء
# ------------------------------------------------------------------------------
def init_tb_database():
    conn = sqlite3.connect("tb_source_ultra_mega.db", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance INTEGER DEFAULT 15000,
            bank_balance INTEGER DEFAULT 100000,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            rank_title TEXT DEFAULT 'مطور أساسي'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tb_group_locks (
            chat_id INTEGER PRIMARY KEY,
            lock_links INTEGER DEFAULT 1,
            lock_usernames INTEGER DEFAULT 1,
            lock_spam INTEGER DEFAULT 1,
            lock_chat INTEGER DEFAULT 0,
            lock_bots INTEGER DEFAULT 1,
            lock_forward INTEGER DEFAULT 1,
            lock_photos INTEGER DEFAULT 1,
            lock_videos INTEGER DEFAULT 1,
            lock_stickers INTEGER DEFAULT 1,
            lock_gifs INTEGER DEFAULT 1,
            lock_pin INTEGER DEFAULT 0,
            lock_contacts INTEGER DEFAULT 1,
            lock_files INTEGER DEFAULT 1,
            lock_voice INTEGER DEFAULT 1,
            lock_tag INTEGER DEFAULT 1,
            lock_arabic INTEGER DEFAULT 0,
            lock_english INTEGER DEFAULT 0,
            lock_badwords INTEGER DEFAULT 1,
            lock_reply INTEGER DEFAULT 0,
            lock_inline INTEGER DEFAULT 1
        )
    """)
    
    conn.commit()
    conn.close()

init_tb_database()

# ------------------------------------------------------------------------------
# محرك الحماية الفائق والحديث (Tb Security V7)
# ------------------------------------------------------------------------------
async def tb_security_engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat:
        return
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    msg = update.message
    text = msg.text or msg.caption or ""
    
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        if member.status in ["administrator", "creator"] or user.id == DEV_ID:
            return
    except:
        pass

    conn = sqlite3.connect("tb_source_ultra_mega.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT lock_links, lock_usernames, lock_spam, lock_chat, lock_forward, 
               lock_photos, lock_videos, lock_stickers, lock_gifs, lock_pin, 
               lock_contacts, lock_files, lock_voice, lock_tag, lock_arabic, 
               lock_english, lock_badwords, lock_reply, lock_inline
        FROM tb_group_locks WHERE chat_id = ?
    """, (chat_id,))
    row = cursor.fetchone()
    if not row:
        locks = (1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1)
    else:
        locks = row
    conn.close()

    l_links, l_user, l_spam, l_chat, l_fwd, l_ph, l_vid, l_stk, l_gif, l_pin, l_cont, l_file, l_voi, l_tag, l_arb, l_eng, l_bad, l_rep, l_inl = locks

    if l_chat == 1:
        try: await msg.delete()
        except: pass
        return

    if l_links == 1 and any(w in text.lower() for w in ["http://", "https://", "t.me/", "www.", ".com", "joinchat", "t.me/joinchat"]):
        try:
            await msg.delete()
            await msg.reply_text(f"⚠️ عذراً [{user.first_name}](tg://user?id={user.id})، ممنوع نشر الروابط!\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="Markdown")
        except: pass
        return

    if l_user == 1 and ("@" in text or "تليكرام" in text):
        try:
            await msg.delete()
            await msg.reply_text(f"⚠️ ممنوع نشر المعرفات هنا [{user.first_name}](tg://user?id={user.id})!\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="Markdown")
        except: pass
        return

    if l_fwd == 1 and (msg.forward_date or msg.forward_from):
        try:
            await msg.delete()
            await msg.reply_text(f"⚠️ ممنوع توجيه الرسائل هنا [{user.first_name}](tg://user?id={user.id})!\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="Markdown")
        except: pass
        return

    if l_ph == 1 and msg.photo:
        try:
            await msg.delete()
            await msg.reply_text(f"⚠️ ممنوع نشر الصور هنا [{user.first_name}](tg://user?id={user.id})!\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="Markdown")
        except: pass
        return

    if l_vid == 1 and msg.video:
        try:
            await msg.delete()
            await msg.reply_text(f"⚠️ ممنوع نشر الفيديوهات هنا [{user.first_name}](tg://user?id={user.id})!\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="Markdown")
        except: pass
        return

    if l_stk == 1 and msg.sticker:
        try:
            await msg.delete()
            await msg.reply_text(f"⚠️ ممنوع الملصقات هنا [{user.first_name}](tg://user?id={user.id})!\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="Markdown")
        except: pass
        return

    if l_gif == 1 and msg.animation:
        try:
            await msg.delete()
            await msg.reply_text(f"⚠️ ممنوع المتحركات هنا [{user.first_name}](tg://user?id={user.id})!\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="Markdown")
        except: pass
        return

    if l_pin == 1 and msg.pinned_message:
        try:
            await msg.delete()
            await msg.reply_text(f"⚠️ التثبيت مقفل في هذه المجموعة!\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="Markdown")
        except: pass
        return

    if l_bad == 1 and any(w in text.lower() for w in ["كس", "طيز", "عهر", "فحش", "منيوك", "قندرة"]):
        try:
            await msg.delete()
            await msg.reply_text(f"⚠️ ممنوع استخدام الألفاظ النابية [{user.first_name}](tg://user?id={user.id})!\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="Markdown")
        except: pass
        return

# ------------------------------------------------------------------------------
# الأوامر المتقدمة، الإدارة، والكلوشات الخاصة بسورس تي بي (Tb)
# ------------------------------------------------------------------------------
async def tb_profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"🪪 **معلومات الملف الشخصي:**\n\n• الاسم: {user.first_name}\n• المعرف: @{user.username or 'لا يوجد'}\n• الأيدي (ID): `{user.id}`\n• الرتبة الحالية: مطور أساسي 👑\n• حقوق السورس: @{DEV_USERNAME}"
    await update.message.reply_text(text, parse_mode="Markdown")

async def tb_pin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text(f"⚠️ يجب الرد على الرسالة المراد تثبيتها!\n• حقوق السورس: @{DEV_USERNAME}")
        return
    try:
        await update.message.reply_to_message.pin()
        chat_id = update.effective_chat.id
        conn = sqlite3.connect("tb_source_ultra_mega.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tb_group_locks SET lock_pin = 1 WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"📌 **تم تثبيت (pin) بنجاح تام في المجموعة.**\n• بواسطة: {update.effective_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ عذراً، لا أملك صلاحية التثبيت أو حدث خطأ: {e}")

async def tb_unpin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.unpin_all_chat_messages(update.effective_chat.id)
        chat_id = update.effective_chat.id
        conn = sqlite3.connect("tb_source_ultra_mega.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tb_group_locks SET lock_pin = 0 WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"🔓 **تم فتح (pin) بنجاح تام في المجموعة.**\n• بواسطة: {update.effective_user.first_name}\n• حقوق السورس: @{DEV_USERNAME}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ عذراً، لا أملك صلاحية إلغاء التثبيت: {e}")

async def tb_mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text(f"⚠️ يجب الرد على الشخص المراد كتمه!\n• حقوق السورس: @{DEV_USERNAME}")
        return
    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id
    try:
        await context.bot.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
        await update.message.reply_text(f"🔇 تم كتم العضو بنجاح!\n• حقوق السورس: @{DEV_USERNAME}")
    except Exception as e:
        await update.message.reply_text(f"❌ لا يمكنني كتم العضو: {e}")

async def tb_unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text(f"⚠️ يجب الرد على الشخص المراد إلغاء كتمه!\n• حقوق السورس: @{DEV_USERNAME}")
        return
    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id
    try:
        await context.bot.restrict_chat_member(chat_id, user_id, ChatPermissions(
            can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True
        ))
        await update.message.reply_text(f"🔊 تم إلغاء كتم العضو بنجاح!\n• حقوق السورس: @{DEV_USERNAME}")
    except Exception as e:
        await update.message.reply_text(f"❌ لا يمكنني إلغاء كتم العضو: {e}")

async def tb_ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text(f"⚠️ يجب الرد على الشخص المراد حظره!\n• حقوق السورس: @{DEV_USERNAME}")
        return
    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id
    try:
        await context.bot.ban_chat_member(chat_id, user_id)
        await update.message.reply_text(f"🔨 تم حظر العضو من المجموعة بنجاح!\n• حقوق السورس: @{DEV_USERNAME}")
    except Exception as e:
        await update.message.reply_text(f"❌ لا يمكنني حظر العضو: {e}")

async def tb_unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text(f"⚠️ يجب الرد على رسالة الشخص المراد إلغاء حظره!\n• حقوق السورس: @{DEV_USERNAME}")
        return
    user_id = update.message.reply_to_message.from_user.id
    chat_id = update.effective_chat.id
    try:
        await context.bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
        await update.message.reply_text(f"🤝 تم إلغاء حظر العضو بنجاح!\n• حقوق السورس: @{DEV_USERNAME}")
    except Exception as e:
        await update.message.reply_text(f"❌ لا يمكنني إلغاء حظر العضو: {e}")

# ------------------------------------------------------------------------------
# لوحة الأوامر المحدثة بالكامل للإصدار 7.0
# ------------------------------------------------------------------------------
async def tb_commands_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛡️ حماية المجموعات الشاملة (م 1)", callback_data="tb_m1")],
        [InlineKeyboardButton("👑 المشرفين والرتب المتقدمة (م 2)", callback_data="tb_m2"),
         InlineKeyboardButton("⚙️ إعدادات البوت والترحيب (م 3)", callback_data="tb_m3")],
        [InlineKeyboardButton("🧹 أوامر التنظيف والمسح (م 4)", callback_data="tb_m4"),
         InlineKeyboardButton("🛠️ لوحة تحكم المطور الخارق (م 5)", callback_data="tb_m5")],
        [InlineKeyboardButton("🎮 الألعاب والترتيب المالي (م 6)", callback_data="tb_m6")],
        [InlineKeyboardButton("🔙 القائمة الرئيسية", callback_data="tb_home")]
    ]
    text = f"⚙️ **سورس تي بي (Tb) الإصدار 7.0 - لوحة التحكم المركزية:**\n\n• تم تحديث كافة الأوامر والمميزات بنجاح.\n• المطور الأساسي: @{DEV_USERNAME}"
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def tb_callbacks_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    back = [[InlineKeyboardButton("🔙 رجوع لقائمة الأوامر", callback_data="tb_back")]]

    if data == "tb_m1":
        msg = f"🛡️ **[ م 1 ] أوامر القفل والفتح المتقدمة:**\n- قفل/فتح: الروابط، المعرفات، التكرار، الصور، الفيديوهات، البوتات، التوجيه، الملصقات، المتحركات، التثبيت، الدردشة، الفحش، الجهات، الملفات، الصوتيات، البصمات، الردود، الانلاين.\n• حقوق السورس: @{DEV_USERNAME}"
    elif data == "tb_m2":
        msg = f"👑 **[ م 2 ] المشرفين والرتب:**\n- رفع مميز، رفع ادمن، رفع مدير، رفع مالك، رفع مطور، تنزيل الكل، قائمة الرتب والمشرفين المعتمدين.\n• حقوق السورس: @{DEV_USERNAME}"
    elif data == "tb_m3":
        msg = f"⚙️ **[ م 3 ] التفعيلات والإشعارات:**\n- تفعيل/تعطيل الترحيب، الردود التلقائية، الإشعارات، روابط الانضمام، الحماية الذكية.\n• حقوق السورس: @{DEV_USERNAME}"
    elif data == "tb_m4":
        msg = f"🧹 **[ م 4 ] المسح والتنظيف الشامل:**\n- مسح الرسائل، تنظيف الصامتين، طرد الحسابات المحذوفة، مسح المكتومين، تنظيف السجل.\n• حقوق السورس: @{DEV_USERNAME}"
    elif data == "tb_m5":
        msg = f"🛠️ **[ م 5 ] أوامر المطور والتحكم الخارق:**\n- الإذاعة العامة (مكتوب، ميديا)، احصائيات البوت، مغادرة المجموعات، تفعيل الصيانة، تحديث النظام.\n• حقوق السورس: @{DEV_USERNAME}"
    elif data == "tb_m6":
        msg = f"🎮 **[ م 6 ] الألعاب والمسابقات الكبرى:**\n- قاعة الألعاب، لعبة الصراحة، زواج، تجميع نقاط، مسابقات أسرع حرف، روليت، حظ.\n• حقوق السورس: @{DEV_USERNAME}"
    elif data == "tb_back":
        await tb_commands_panel(update, context)
        return
    elif data == "tb_home":
        await query.edit_message_text(f"🏠 القائمة الرئيسية لسورس تي بي (Tb) الإصدار 7.0.\n• حقوق السورس: @{DEV_USERNAME}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 عرض الأوامر الشاملة", callback_data="tb_m1")]]))
        return
    else:
        return
    await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(back), parse_mode="Markdown")

# ------------------------------------------------------------------------------
# معالج الرسائل والنصي
# ------------------------------------------------------------------------------
async def tb_message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    await tb_security_engine(update, context)
    text = update.message.text.strip()
    lower = text.lower()

    if lower in ["الاوامر", "الأوامر", "اوامر", "أوامر"]:
        await tb_commands_panel(update, context)
        return
    elif lower in ["تفعيل التثبيت", "قفل التثبيت", "تثبيت"]:
        await tb_pin_command(update, context)
        return
    elif lower in ["فتح التثبيت", "تعطيل التثبيت", "فتح تثبيت"]:
        await tb_unpin_command(update, context)
        return
    elif lower in ["معلوماتي", "الملف الشخصي", "ايادي"]:
        await tb_profile_command(update, context)
        return
    elif lower in ["كتم"]:
        await tb_mute_command(update, context)
        return
    elif lower in ["الغاء كتم", "إلغاء كتم"]:
        await tb_unmute_command(update, context)
        return
    elif lower in ["حظر"]:
        await tb_ban_command(update, context)
        return
    elif lower in ["الغاء حظر", "إلغاء حظر", "فك حظر"]:
        await tb_unban_command(update, context)
        return

# ------------------------------------------------------------------------------
# التشغيل الرئيسي للبوت
# ------------------------------------------------------------------------------
def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ يرجى تعيين التوكن الحقيقي للبوت في المتغير!")
        return

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", tb_commands_panel))
    app.add_handler(CommandHandler(["الاوامر", "الأوامر", "اوامر", "أوامر"], tb_commands_panel))
    app.add_handler(CommandHandler("pin", tb_pin_command))
    app.add_handler(CommandHandler("unpin", tb_unpin_command))
    app.add_handler(CommandHandler("profile", tb_profile_command))
    app.add_handler(CommandHandler("mute", tb_mute_command))
    app.add_handler(CommandHandler("unmute", tb_unmute_command))
    app.add_handler(CommandHandler("ban", tb_ban_command))
    app.add_handler(CommandHandler("unban", tb_unban_command))

    app.add_handler(CallbackQueryHandler(tb_callbacks_handler, pattern="^tb_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tb_message_router))

    logger.info("🚀 سورس تي بي (Tb) الإصدار 7.0 الأسطوري يعمل بكفاءة تامة وبدون ردود عشوائية...")
    while True:
        try:
            app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
        except Exception as e:
            logger.error(f"⚠️ خطأ بالاتصال، إعادة تشغيل: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
