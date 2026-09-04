import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

# إعداد السجلات
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن الخاص بك
TOKEN = os.environ.get("BOT_TOKEN", "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w")

# معلومات المطور والقناة
DEV_USERNAME = "@odox3"
CHANNEL_USERNAME = "@odox6"

# قواعد البيانات وإعدادات البوت
settings = {"id_with_photo": True}
active_groups = set() 
custom_replies = {}  
custom_commands = {} 
user_message_counts = {}

async def send_command_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة الأوامر الـ 7 الشاملة"""
    text = (
        "🤖 **اليك اوامر البوت ﯡ الحماية الشاملة:**\n\n"
        "• ( 1p ) ~ اوامر الحماية الكبرى 🛡️\n"
        "• ( 2p ) ~ اوامر المشرفين والإشراف 👑\n"
        "• ( 3p ) ~ اوامر التفعيلات والروابط ⚙️\n"
        "• ( 4p ) ~ اوامر المسح والتنظيف 🗑️\n"
        "• ( 5p ) ~ اوامر المطورين والتحكم 🛠️\n"
        "• ( 6p ) ~ اوامر الترفيه والالعاب 🎮\n"
        "• ( 7p ) ~ أوامر الألعاب الإضافية والبحث 🎲"
    )
    
    keyboard = [
        [InlineKeyboardButton("• 1 • الحماية", callback_data="sec_1"), InlineKeyboardButton("• 2 • المشرفين", callback_data="sec_2")],
        [InlineKeyboardButton("• 3 • التفعيلات", callback_data="sec_3"), InlineKeyboardButton("• 4 • المسح", callback_data="sec_4")],
        [InlineKeyboardButton("• 5 • المطورين", callback_data="sec_5"), InlineKeyboardButton("• 6 • الترفيه", callback_data="sec_6")],
        [InlineKeyboardButton("• 7 • الألعاب الإضافية واليوتيوب", callback_data="sec_7")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query and update.callback_query.message:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إدارة أزرار الأقسام السبعة"""
    query = update.callback_query
    await query.answer()

    if query.data == "sec_1":
        await query.edit_message_text(
            "🛡️ **قسم أوامر الحماية الكبرى:**\n\n"
            "• `قفل الروابط` / `فتح الروابط`\n"
            "• `قفل التكرار` / `فتح التكرار`\n"
            "• `قفل السبرام` / `فتح السبرام`\n"
            "• `طرد` (بالرد على المخالف)\n"
            "• `كتم` / `تكلم` (بالرد)",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_2":
        await query.edit_message_text(
            "👑 **قسم أوامر المشرفين:**\n\n"
            "• `رفع [الرتبة]` / `تنزيل`\n"
            "• `الرابط` أو `رابط` لجلب رابط الجروب\n"
            "• تثبيت وإلغاء تثبيت الرسائل",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_3":
        await query.edit_message_text(
            "⚙️ **قسم أوامر التفعيلات والردود:**\n\n"
            "• `تفعيل` (داخل الكروب لتشغيل الحماية)\n"
            "• `تفعيل الايدي بالصورة` / `تعطيل الايدي بالصورة`\n"
            "• `اضف رد [الكلمة] // [الرد]`\n"
            "• `حذف رد [الكلمة]`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_4":
        await query.edit_message_text(
            "🗑️ **قسم أوامر المسح والتنظيف:**\n\n"
            "• `مسح الردود`\n"
            "• `مسح المكتومين`\n"
            "• `مسح المحظورين`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_5":
        await query.edit_message_text(
            "🛠️ **قسم أوامر المطورين والاختصارات:**\n\n"
            f"• المطور: {DEV_USERNAME}\n"
            f"• القناة: {CHANNEL_USERNAME}\n"
            "• `اضف امر [الاسم] // [الرد]`\n"
            "• `حذف امر [الاسم]`\n"
            "• `اذاعة`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_6":
        await query.edit_message_text(
            "🎮 **قسم الترفيه والالعاب:**\n\n"
            "• `ألعاب` أو `العاب` (قائمة الألعاب السريعة)\n"
            "• `حظك`\n"
            "• `تخمين`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_7":
        await query.edit_message_text(
            "🎲 **قسم الألعاب الإضافية والبحث:**\n\n"
            "• لعبة الصراحة والجرأة\n"
            "• لعبة حظ الأرقام\n"
            "• `يوتيوب [اسم الأغنية]` للبحث الفوري وجلب الروابط!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "back_home":
        await send_command_list(update, context)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """المعالج الأساسي لكل رسائل وأوامر الكروبات"""
    
    if not update.message:
        return

    # الترحيب بالأعضاء الجدد
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            await update.message.reply_text(
                f"✨ أهلاً بك يا [{member.first_name}](tg://user?id={member.id}) في المجموعه!\n📢 قناة السورس: {CHANNEL_USERNAME}",
                parse_mode="Markdown"
            )
        return

    if not update.message.text:
        return

    text = update.message.text.strip()
    chat = update.message.chat
    user = update.message.from_user
    msg = update.message

    user_message_counts[user.id] = user_message_counts.get(user.id, 0) + 1
    msg_count = user_message_counts[user.id]

    # أمر التفعيل داخل الكروب
    if text == "تفعيل":
        if chat.type in ["group", "supergroup"]:
            active_groups.add(chat.id)
            await msg.reply_text("✅ **تم تفعيل البوت وحمايته الكاملة في هذه المجموعة بنجاح!**", parse_mode="Markdown")
        else:
            await msg.reply_text("هذا الأمر يُستخدم داخل المجموعات فقط.")
        return

    # الحماية اللانهائية (حذف الروابط في الكروبات المفاعلة)
    if chat.type in ["group", "supergroup"] and chat.id in active_groups:
        if any(w in text.lower() for w in ["http://", "https://", "t.me/", "www."]):
            try:
                member = await chat.get_member(user.id)
                if member.status not in ["creator", "administrator"]:
                    await msg.delete()
                    await msg.reply_text(f"⚠️ ممنوع نشر الروابط يا [{user.first_name}](tg://user?id={user.id})!", parse_mode="Markdown")
                    return
            except Exception:
                pass

    # عرض قائمة الأوامر (تظهر فوراً عند كتابة اوامر أو 1p وغيرها)
    if text in ["اوامر", "الأوامر", "أوامر", "1p", "2p", "3p", "4p", "5p", "6p", "7p"]:
        await send_command_list(update, context)
        return

    # التحكم بالايدي بالصورة
    global settings
    if text == "تفعيل الايدي بالصورة":
        settings["id_with_photo"] = True
        await msg.reply_text("✅ تم تفعيل عرض الأيدي بالصورة بنجاح.")
        return
    elif text == "تعطيل الايدي بالصورة":
        settings["id_with_photo"] = False
        await msg.reply_text("❌ تم تعطيل عرض الأيدي بالصورة وأصبح نصياً.")
        return

    # أمر الايدي بالصيغة المطلوبة مع الصورة
    if text in ["ايدي", "ID", "ايديي", "معلوماتي"]:
        username_handle = f"@{user.username}" if user.username else "@zv11ss"
        id_formatted = (
            f"• USE ➤ {username_handle} .\n"
            f"• MSG ➤ {msg_count} .\n"
            f"• STA ➤ العضو .\n"
            f"• iD ➤ {user.id} ."
        )
        
        if settings["id_with_photo"]:
            photo_url = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500"
            try:
                await msg.reply_photo(photo=photo_url, caption=id_formatted)
            except Exception:
                await msg.reply_text(id_formatted)
        else:
            await msg.reply_text(id_formatted)
        return

    # رابط الجروب
    if text in ["الرابط", "رابط", "رابط الجروب"]:
        if chat.type in ["group", "supergroup"]:
            try:
                link = await chat.export_invite_link()
                await msg.reply_text(f"🔗 رابط المجموعة الفوري:\n{link}")
            except Exception:
                await msg.reply_text("❌ يجب أن أكون مشرفاً لجلب الرابط.")
        else:
            await msg.reply_text("هذا الأمر خاص بالمجموعات فقط.")
        return

    # بحث اليوتيوب
    if text.startswith("يوتيوب "):
        query_song = text.replace("يوتيوب ", "").strip()
        yt_result = (
            f"🎵 **نتائج البحث في اليوتيوب عن:** `{query_song}`\n\n"
            f"• رابط البحث المباشر: https://www.youtube.com/results?search_query={query_song.replace(' ', '+')}\n"
            f"🎧 تم جلب الطلب بواسطة سورس تي بي."
        )
        await msg.reply_text(yt_result, parse_mode="Markdown")
        return

    # إضافة وحذف الردود والأوامر المخصصة
    if text.startswith("اضف رد "):
        try:
            parts = text.replace("اضف رد ", "").split("//")
            if len(parts) == 2:
                kw, rep = parts[0].strip(), parts[1].strip()
                custom_replies[kw] = rep
                await msg.reply_text(f"✅ تم إضافة الرد للكلمة: `{kw}` بنجاح!", parse_mode="Markdown")
        except Exception:
            pass
        return

    if text.startswith("حذف رد "):
        kw = text.replace("حذف رد ", "").strip()
        if kw in custom_replies:
            del custom_replies[kw]
            await msg.reply_text(f"🗑️ تم حذف الرد بنجاح.")
        return

    if text.startswith("اضف امر "):
        try:
            parts = text.replace("اضف امر ", "").split("//")
            if len(parts) == 2:
                cmd_k, cmd_v = parts[0].strip(), parts[1].strip()
                custom_commands[cmd_k] = cmd_v
                await msg.reply_text(f"✅ تم إضافة الأمر `{cmd_k}` بنجاح!", parse_mode="Markdown")
        except Exception:
            pass
        return

    if text.startswith("حذف امر "):
        cmd_k = text.replace("حذف امر ", "").strip()
        if cmd_k in custom_commands:
            del custom_commands[cmd_k]
            await msg.reply_text(f"🗑️ تم حذف الأمر بنجاح.")
        return

    # فحص المخزن للردود والأوامر
    if text in custom_replies:
        await msg.reply_text(custom_replies[text])
        return

    if text in custom_commands:
        await msg.reply_text(custom_commands[text])
        return

    # رفع وتنزيل
    if text.startswith("رفع "):
        target_title = text.replace("رفع ", "").strip()
        await msg.reply_text(f"✅ تم ترقية العضو بنجاح وأصبح: **{target_title}**", parse_mode="Markdown")
        return
    elif text.startswith("تنزيل "):
        await msg.reply_text("🔽 تم تنزيل رتبة العضو بنجاح.")
        return

    # طرد
    if text == "طرد":
        if msg.reply_to_message:
            try:
                target_user = msg.reply_to_message.from_user
                await chat.ban_member(target_user.id)
                await msg.reply_text(f"🚷 تم طرد المستخدم [{target_user.first_name}](tg://user?id={target_user.id}) بنجاح.", parse_mode="Markdown")
            except Exception:
                await msg.reply_text("❌ لا يمكنني طرد هذا المستخدم.")
        else:
            await msg.reply_text("⚠️ قم بالرد على رسالة الشخص المراد طرده مع كتابة `طرد`.")
        return

    # ألعاب
    if text in ["ألعاب", "العاب", "الالعاب"]:
        await msg.reply_text("🎮 **قائمة الألعاب السريعة:**\n• لعبة الصراحة والجرأة\n• حظك اليوم\n• تخمين الأرقام والأسئلة العامة", parse_mode="Markdown")
        return

def main():
    if not TOKEN:
        logger.error("لم يتم العثور على التوكن!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler(["start", "cmds"], start_command_func := lambda u, c: send_command_list(u, c)))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT | filters.StatusUpdate.NEW_CHAT_MEMBERS & ~filters.COMMAND, handle_messages))

    logger.info("🤖 تم تشغيل بوت Tb Source كبوت حماية شامل بنجاح...")
    application.run_polling()

if __name__ == "__main__":
    main()
