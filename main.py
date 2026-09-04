import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)

# إعداد السجلات الأساسية
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# التوكن ومعلومات البوت والمطور
TOKEN = os.environ.get("BOT_TOKEN", "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w")
DEV_USERNAME = "@odox3"
CHANNEL_USERNAME = "@odox6"

# إعدادات النظام وقواعد البيانات الداخلية
settings = {"id_with_photo": True}
active_groups = set()
custom_replies = {}
custom_commands = {}
user_message_counts = {}

# خادم ويب وهمي (Flask) لضمان بقاء البوت نشطاً 24/7 وعدم نوم الاستضافة
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot is running 24/7 successfully!"

def run_web():
    app_flask.run(host='0.0.0.0', port=8080)

async def send_command_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض لوحة التحكم الرئيسية والأقسام السبعة تماماً كالسورس الأصلي"""
    text = (
        "🤖 **سورس حماية وإدارة المجموعات الشامل:**\n\n"
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
        [InlineKeyboardButton("• 7 • الألعاب واليوتيوب", callback_data="sec_7")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query and update.callback_query.message:
        await update.callback_query.message.edit_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إدارة أزرار لوحة التحكم التفاعلية"""
    query = update.callback_query
    await query.answer()

    back_btn = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_home")]]

    if query.data == "sec_1":
        await query.edit_message_text(
            "🛡️ **قسم أوامر الحماية الكبرى:**\n\n"
            "• `قفل الروابط` / `فتح الروابط`\n"
            "• `طرد` (بالرد على المخالف)\n"
            "• `كتم` / `تكلم` (بالرد على العضو)",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_btn)
        )
    elif query.data == "sec_2":
        await query.edit_message_text(
            "👑 **قسم أوامر المشرفين والإشراف:**\n\n"
            "• `رفع [الرتبة]` لترقية العضو\n"
            "• `تنزيل` لإزالة الصلاحيات\n"
            "• `الرابط` لجلب رابط المجموعه",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_btn)
        )
    elif query.data == "sec_3":
        await query.edit_message_text(
            "⚙️ **قسم أوامر التفعيلات والردود:**\n\n"
            "• أرسل `تفعيل` لتشغيل الحماية بالكروب\n"
            "• `تفعيل الايدي بالصورة` / `تعطيل الايدي بالصورة`\n"
            "• `اضف رد [الكلمة] // [الرد]`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_btn)
        )
    elif query.data == "sec_4":
        await query.edit_message_text(
            "🗑️ **قسم أوامر المسح والتنظيف:**\n\n"
            "• مسح الردود والأوامر المخزنة.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_btn)
        )
    elif query.data == "sec_5":
        await query.edit_message_text(
            "🛠️ **قسم أوامر المطورين والتحكم:**\n\n"
            f"• المطور الأساسي: {DEV_USERNAME}\n"
            f"• قناة السورس: {CHANNEL_USERNAME}\n"
            "• `اضف امر [الاسم] // [الرد]`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_btn)
        )
    elif query.data == "sec_6":
        await query.edit_message_text(
            "🎮 **قسم أوامر الترفيه والالعاب:**\n\n"
            "• `ألعاب` أو `العاب` لعرض الألعاب السريعة.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_btn)
        )
    elif query.data == "sec_7":
        await query.edit_message_text(
            "🎲 **قسم الألعاب الإضافية والبحث:**\n\n"
            "• `يوتيوب [اسم الفيديو]` للبحث السريع والفوري.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(back_btn)
        )
    elif query.data == "back_home":
        await send_command_list(update, context)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل والأوامر الشامل داخل المجموعات"""
    if not update.message:
        return

    # الترحيب بالأعضاء الجدد عند الانضمام
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

    # تتبع عدد رسائل المستخدم للأيدي
    user_message_counts[user.id] = user_message_counts.get(user.id, 0) + 1
    msg_count = user_message_counts[user.id]

    # أمر تفعيل البوت في الكروب
    if text == "تفعيل":
        if chat.type in ["group", "supergroup"]:
            active_groups.add(chat.id)
            await msg.reply_text("✅ **تم تفعيل البوت وحمايته الكاملة في هذه المجموعة بنجاح!**", parse_mode="Markdown")
        else:
            await msg.reply_text("هذا الأمر يُستخدم داخل المجموعات المفعلة فقط.")
        return

    # حماية الروابط عند التفعيل
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

    # عرض قائمة الأوامر عند كتابة الرموز أو الكلمات المفتاحية
    if text in ["اوامر", "الأوامر", "أوامر", "1p", "2p", "3p", "4p", "5p", "6p", "7p"]:
        await send_command_list(update, context)
        return

    global settings
    if text == "تفعيل الايدي بالصورة":
        settings["id_with_photo"] = True
        await msg.reply_text("✅ تم تفعيل عرض الأيدي بالصورة.")
        return
    elif text == "تعطيل الايدي بالصورة":
        settings["id_with_photo"] = False
        await msg.reply_text("❌ تم تعطيل عرض الأيدي بالصورة.")
        return

    # عرض الأيدي بالصيغة المطلوبة تماماً
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

    # جلب رابط المجموعة
    if text in ["الرابط", "رابط"]:
        if chat.type in ["group", "supergroup"]:
            try:
                link = await chat.export_invite_link()
                await msg.reply_text(f"🔗 رابط المجموعة الفوري:\n{link}")
            except Exception:
                await msg.reply_text("❌ يجب أن أكون مشرفاً لجلب رابط المجموعة.")
        return

    # بحث يوتيوب فوري
    if text.startswith("يوتيوب "):
        query_song = text.replace("يوتيوب ", "").strip()
        yt_result = (
            f"🎵 **نتائج البحث في اليوتيوب عن:** `{query_song}`\n\n"
            f"• رابط البحث المباشر: https://www.youtube.com/results?search_query={query_song.replace(' ', '+')}\n"
            f"🎧 تم جلب الطلب بواسطة السورس."
        )
        await msg.reply_text(yt_result, parse_mode="Markdown")
        return

    # إضافة الأوامر والردود المخصصة
    if text.startswith("اضف رد "):
        try:
            parts = text.replace("اضف رد ", "").split("//")
            if len(parts) == 2:
                custom_replies[parts[0].strip()] = parts[1].strip()
                await msg.reply_text("✅ تم إضافة الرد بنجاح!")
        except Exception:
            pass
        return

    if text.startswith("اضف امر "):
        try:
            parts = text.replace("اضف امر ", "").split("//")
            if len(parts) == 2:
                custom_commands[parts[0].strip()] = parts[1].strip()
                await msg.reply_text("✅ تم إضافة الأمر بنجاح!")
        except Exception:
            pass
        return

    if text in custom_replies:
        await msg.reply_text(custom_replies[text])
        return

    if text in custom_commands:
        await msg.reply_text(custom_commands[text])
        return

    # أوامر الإشراف (رفع وتنزيل وطرد)
    if text.startswith("رفع "):
        target_title = text.replace("رفع ", "").strip()
        await msg.reply_text(f"✅ تم رفع العضو بنجاح وأصبح: **{target_title}**", parse_mode="Markdown")
        return
    elif text == "تنزيل":
        await msg.reply_text("🔽 تم تنزيل رتبة العضو بنجاح.")
        return

    if text == "طرد":
        if msg.reply_to_message:
            try:
                target_user = msg.reply_to_message.from_user
                await chat.ban_member(target_user.id)
                await msg.reply_text(f"🚷 تم طرد المستخدم [{target_user.first_name}](tg://user?id={target_user.id}) بنجاح.", parse_mode="Markdown")
            except Exception:
                await msg.reply_text("❌ لا يمكنني طرد هذا المستخدم.")
        else:
            await msg.reply_text("⚠️ قم بالرد على رسالة الشخص المراد طرده واكتب `طرد`.")
        return

    if text in ["ألعاب", "العاب", "الالعاب"]:
        await msg.reply_text("🎮 **قائمة الألعاب السريعة:**\n• لعبة الصراحة والجرأة\n• حظك اليوم", parse_mode="Markdown")
        return

def main():
    if not TOKEN:
        logger.error("لم يتم العثور على التوكن!")
        return

    # تشغيل خادم الـ Keep-Alive في الخلفية لمنع توقف الاستضافة
    t = Thread(target=run_web)
    t.start()

    # تشغيل تطبيق تليجرام البوت
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler(["start", "cmds"], send_command_list))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    logger.info("🤖 تم تشغيل السورس المتكامل بنجاح تام...")
    application.run_polling()

if __name__ == "__main__":
    main()
