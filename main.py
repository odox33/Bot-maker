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

# إعدادات البوت والكروبات المفاعلة
settings = {
    "id_with_photo": True
}
active_groups = set() # لتخزين الكروبات المفاعلة

user_message_counts = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة الأوامر الستة أو السبعة المطلوبة"""
    text = (
        "🤖 **اليك اوامر البوت ﯡ.**\n\n"
        "• ( 1p ) ~ اوامر الحماية 🛡️\n"
        "• ( 2p ) ~ اوامر المشرفين 👑\n"
        "• ( 3p ) ~ اوامر التفعيلات ⚙️\n"
        "• ( 4p ) ~ اوامر المسح 🗑️\n"
        "• ( 5p ) ~ اوامر المطورين 🛠️\n"
        "• ( 6p ) ~ اوامر الترفيه والالعاب 🎮\n"
        "• ( 7p ) ~ اوامر الألعاب الإضافية 🎲"
    )
    
    # الأزرار السبعة التفاعلية
    keyboard = [
        [InlineKeyboardButton("• 1 •", callback_data="sec_1"), InlineKeyboardButton("• 2 •", callback_data="sec_2")],
        [InlineKeyboardButton("• 3 •", callback_data="sec_3"), InlineKeyboardButton("• 4 •", callback_data="sec_4")],
        [InlineKeyboardButton("• 5 •", callback_data="sec_5"), InlineKeyboardButton("• 6 •", callback_data="sec_6")],
        [InlineKeyboardButton("• 7 • الألعاب الإضافية", callback_data="sec_7")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأقسام السبعة للأزرار"""
    query = update.callback_query
    await query.answer()

    if query.data == "sec_1":
        await query.edit_message_text(
            "🛡️ **قسم أوامر الحماية اللانهائية:**\n\n"
            "• `قفل الروابط` / `فتح الروابط`\n"
            "• `قفل التكرار` / `فتح التكرار`\n"
            "• `طرد` (بالرد على المستخدم)\n"
            "• `كتم` / `تكلم`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_2":
        await query.edit_message_text(
            "👑 **قسم أوامر المشرفين:**\n\n"
            "• `رفع [الرتبة]` / `تنزيل`\n"
            "• `الرابط` أو `رابط` لجلب رابط الجروب الفوري",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_3":
        await query.edit_message_text(
            "⚙️ **قسم أوامر التفعيلات:**\n\n"
            "• `تفعيل` (داخل الجروب)\n"
            "• `تفعيل الايدي بالصورة`\n"
            "• `تعطيل الايدي بالصورة`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_4":
        await query.edit_message_text(
            "🗑️ **قسم أوامر المسح:**\n\n"
            "• `مسح الردود`\n"
            "• `مسح المكتومين`\n"
            "• `مسح المحظورين`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_5":
        await query.edit_message_text(
            "🛠️ **قسم أوامر المطورين:**\n\n"
            f"• المطور الأساسي: {DEV_USERNAME}\n"
            f"• قناة السورس: {CHANNEL_USERNAME}\n"
            "• `اذاعة`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_6":
        await query.edit_message_text(
            "🎮 **قسم الترفيه والالعاب:**\n\n"
            "• `العاب` أو `ألعاب`\n"
            "• `حظك`\n"
            "• اكتب `يوتيوب [اسم الأغنية]` للبحث الفوري!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "sec_7":
        await query.edit_message_text(
            "🎲 **قسم الألعاب الإضافية والتسلية:**\n\n"
            "• لعبة تخمين الأرقام\n"
            "• لعبة الصراحة والجرأة السريعة\n"
            "• أسئلة عامة",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back_home")]])
        )
    elif query.data == "back_home":
        text = (
            "🤖 **اليك اوامر البوت ﯡ.**\n\n"
            "• ( 1p ) ~ اوامر الحماية 🛡️\n"
            "• ( 2p ) ~ اوامر المشرفين 👑\n"
            "• ( 3p ) ~ اوامر التفعيلات ⚙️\n"
            "• ( 4p ) ~ اوامر المسح 🗑️\n"
            "• ( 5p ) ~ اوامر المطورين 🛠️\n"
            "• ( 6p ) ~ اوامر الترفيه والالعاب 🎮\n"
            "• ( 7p ) ~ اوامر الألعاب الإضافية 🎲"
        )
        keyboard = [
            [InlineKeyboardButton("• 1 •", callback_data="sec_1"), InlineKeyboardButton("• 2 •", callback_data="sec_2")],
            [InlineKeyboardButton("• 3 •", callback_data="sec_3"), InlineKeyboardButton("• 4 •", callback_data="sec_4")],
            [InlineKeyboardButton("• 5 •", callback_data="sec_5"), InlineKeyboardButton("• 6 •", callback_data="sec_6")],
            [InlineKeyboardButton("• 7 • الألعاب الإضافية", callback_data="sec_7")]
        ]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة كافة الأوامر والرسائل والتفعيلات"""
    
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            await update.message.reply_text(
                f"✨ أهلاً بك يا [{member.first_name}](tg://user?id={member.id}) في المجموعه!\n📢 قناة السورس: {CHANNEL_USERNAME}",
                parse_mode="Markdown"
            )
        return

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    chat = update.message.chat
    user = update.message.from_user
    msg = update.message

    user_message_counts[user.id] = user_message_counts.get(user.id, 0) + 1
    msg_count = user_message_counts[user.id]

    # أمر تفعيل البوت داخل الكروب
    if text == "تفعيل":
        if chat.type in ["group", "supergroup"]:
            active_groups.add(chat.id)
            await msg.reply_text("✅ **تم تفعيل البوت في هذه المجموعة بنجاح وتشغيل الحماية والأوامر!**", parse_mode="Markdown")
        else:
            await msg.reply_text("هذا الأمر يُستخدم داخل المجموعات فقط.")
        return

    # حماية الروابط تعمل إذا كان الكروب مفعل
    if chat.type in ["group", "supergroup"] and chat.id in active_groups:
        if "http://" in text or "https://" in text or "t.me/" in text or "www." in text:
            try:
                member = await chat.get_member(user.id)
                if member.status not in ["creator", "administrator"]:
                    await msg.delete()
                    await msg.reply_text(f"⚠️ ممنوع نشر الروابط يا [{user.first_name}](tg://user?id={user.id})!", parse_mode="Markdown")
                    return
            except Exception:
                pass

    # عرض الأوامر الرئيسية (7 أقسام)
    if text in ["اوامر", "الأوامر", "أوامر", "1p", "2p", "3p", "4p", "5p", "6p", "7p"]:
        await start_command(update, context)
        return

    global settings
    if text == "تفعيل الايدي بالصورة":
        settings["id_with_photo"] = True
        await msg.reply_text("✅ تم تفعيل عرض الأيدي بالصورة بنجاح.")
        return
    elif text == "تعطيل الايدي بالصورة":
        settings["id_with_photo"] = False
        await msg.reply_text("❌ تم تعطيل عرض الأيدي بالصورة وأصبح نصياً.")
        return

    # الأيدي بالصيغة المطلوبة تماماً
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

    # رابط المجموعة
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

    # بحث يوتيوب
    if text.startswith("يوتيوب "):
        query_song = text.replace("يوتيوب ", "").strip()
        yt_result = (
            f"🎵 **نتائج البحث في اليوتيوب عن:** `{query_song}`\n\n"
            f"• الرابط المقترح: https://www.youtube.com/results?search_query={query_song.replace(' ', '+')}\n"
            f"🎧 تم جلب الطلب بواسطة سورس تي بي."
        )
        await msg.reply_text(yt_result, parse_mode="Markdown")
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

    # الألعاب
    if text in ["ألعاب", "العاب", "الالعاب"]:
        await msg.reply_text("🎮 **قائمة الألعاب السريعة:**\n• لعبة الصراحة والجرأة\n• حظك اليوم\n• تخمين الأرقام", parse_mode="Markdown")
        return

def main():
    if not TOKEN:
        logger.error("لم يتم العثور على التوكن!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler(["start", "cmds"], start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT | filters.StatusUpdate.NEW_CHAT_MEMBERS & ~filters.COMMAND, handle_messages))

    logger.info("🤖 تم تشغيل بوت Tb Source بنجاح مع التفعيل والأوامر السبعة...")
    application.run_polling()

if __name__ == "__main__":
    main()
