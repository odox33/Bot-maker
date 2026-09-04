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

# إعداد السجلات لمتابعة حالة البوت
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# التوكن الخاص بك
TOKEN = os.environ.get("BOT_TOKEN", "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w")

# معلومات المطور والقناة
DEV_USERNAME = "@odox3"
CHANNEL_USERNAME = "@odox6"

# قواميس التخزين المؤقت للردود والأوامر المضافة
custom_replies = {}  
custom_commands = {} 

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الواجهة والأوامر الأساسية لـ Tb Source مع لوحة المطور"""
    text = (
        "🤖 **مرحباً بك في لوحة تحكم Tb Source**\n\n"
        "إليك قائمة الأوامر والخدمات الأساسية:\n"
        "1️⃣ `/start` أو `اوامر` - عرض لوحة الأوامر الرئيسية\n"
        "2️⃣ `الرابط` - جلب رابط المجموعة (للإداريين)\n"
        "3️⃣ `المنشئين` - عرض قائمة المنشئين الأساسيين\n"
        "4️⃣ `ايدي` أو `ID` - معرفة معلوماتك الشخصية والأيدي\n"
        "5️⃣ `اضف رد [الكلمة] // [الرد]` - إضافة رد تلقائي جديد\n"
        "6️⃣ `حذف رد [الكلمة]` - حذف رد تلقائي\n"
        "7️⃣ `اضف امر [الامر] // [الرد]` - إضافة أمر مخصص\n"
        "• `حذف امر [الامر]` - حذف أمر مخصص\n\n"
        "🛡️ *ميزة الحماية مفعلة تلقائياً (منع الروابط في المجموعات)*"
    )
    
    # أزرار شفافة تفاعلية للوحة المطور وقناة السورس
    keyboard = [
        [InlineKeyboardButton("👑 لوحة المطور وصنع البوتات", callback_data="dev_panel")],
        [InlineKeyboardButton("📢 قناة سورس تي بي (Tb Source)", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التعامل مع الأزرار الشفافة ولوحة المطور"""
    query = update.callback_query
    await query.answer()

    if query.data == "dev_panel":
        dev_text = (
            "🛠 **مرحباً بك في لوحة مطور سورس تي بي (Tb Source)**\n\n"
            "اختر نوع الخدمة التي تريدها:\n\n"
            "🤖 **1. صنع بوت مجاني:**\n"
            "• يستطيع المستخدم إنشاء بوت خاص به مجاناً.\n"
            "• **ملاحظة:** يتم وضع حقوق السورس وتوقيعنا تلقائياً داخل البوت المصنوع.\n"
            f"• للتواصل أو الاستفسار: {DEV_USERNAME}\n\n"
            "💎 **2. صنع بوت مدفوع (بدون حقوق):**\n"
            "• بوت احترافي متكامل وبدون أي حقوق تذكر.\n"
            f"• تتطلب هذه الخدمة مراسلتي حصراً لتنفيذها: [اضغط هنا لمراسلة المطور](https://t.me/{DEV_USERNAME.replace('@', '')})"
        )
        
        keyboard = [
            [InlineKeyboardButton("🤖 صنع بوت مجاني (مع الحقوق)", callback_data="free_bot")],
            [InlineKeyboardButton("💎 صنع بوت مدفوع (بدون حقوق)", callback_data="paid_bot")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(dev_text, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=True)

    elif query.data == "free_bot":
        await query.message.reply_text(
            f"🤖 **قسم صنع البوتات المجانية:**\n\n"
            f"لصنع بوتك المجاني الآن، يرجى إرسال التوكن الخاص بـ BotFather مع إبقاء حقوق سورس تي بي ({CHANNEL_USERNAME}).\n"
            f"لأي استفسار راسل المطور: {DEV_USERNAME}",
            parse_mode="Markdown"
        )

    elif query.data == "paid_bot":
        await query.message.reply_text(
            f"💎 **قسم صنع البوتات المدفوعة:**\n\n"
            f"البوتات المدفوعة تكون **بدون حقوق تماماً** وتتطلب إشرافاً مباشراً.\n"
            f"لطلب بوتك المدفوع، يرجى مراسلة المطور حصراً عبر المعرف الآتي: {DEV_USERNAME}",
            parse_mode="Markdown"
        )

    elif query.data == "back_home":
        text = (
            "🤖 **مرحباً بك في لوحة تحكم Tb Source**\n\n"
            "إليك قائمة الأوامر والخدمات الأساسية:\n"
            "1️⃣ `/start` أو `اوامر` - عرض لوحة الأوامر الرئيسية\n"
            "2️⃣ `الرابط` - جلب رابط المجموعة\n"
            "3️⃣ `المنشئين` - عرض قائمة المنشئين الأساسيين\n"
            "4️⃣ `ايدي` - معرفة معلوماتك الشخصية\n"
            "5️⃣ `اضف رد [الكلمة] // [الرد]`\n"
            "6️⃣ `حذف رد [الكلمة]`\n"
            "7️⃣ `اضف امر [الامر] // [الرد]`"
        )
        keyboard = [
            [InlineKeyboardButton("👑 لوحة المطور وصنع البوتات", callback_data="dev_panel")],
            [InlineKeyboardButton("📢 قناة سورس تي بي (Tb Source)", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل، الحماية، الأوامر الأساسية، وإدارة الإضافات"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    chat = update.message.chat
    user = update.message.from_user
    msg = update.message

    # 1. نظام حماية المجموعات (منع الروابط)
    if chat.type in ["group", "supergroup"]:
        if "http://" in text or "https://" in text or "t.me/" in text or "www." in text:
            try:
                member = await chat.get_member(user.id)
                if member.status not in ["creator", "administrator"]:
                    await msg.delete()
                    await chat.send_message(
                        f"⚠️ عذراً يا [{user.first_name}](tg://user?id={user.id})، ممنوع نشر الروابط في هذه المجموعة!",
                        parse_mode="Markdown"
                    )
                    return
            except Exception:
                pass

    # 2. الأوامر الأساسية
    if text in ["اوامر", "الأوامر", "الالاوامر", "أوامر", "الاوامر"]:
        await start_command(update, context)
        return
        
    elif text in ["الرابط", "رابط الجروب", "رابط"]:
        if chat.type in ["group", "supergroup"]:
            try:
                link = await chat.export_invite_link()
                await msg.reply_text(f"🔗 رابط المجموعة:\n{link}")
            except Exception:
                await msg.reply_text("❌ عذراً، ليس لدي صلاحية جلب الرابط (يجب أن أكون مشرفاً).")
        else:
            await msg.reply_text("هذا الأمر مخصص للمجموعات فقط!")
        return
        
    elif text in ["المنشئين", "المنشئين الاساسيين", "المطور", "المطورين"]:
        devs_info = (
            f"👑 **قائمة المنشئين الأساسيين لـ Tb Source:**\n"
            f"• المطور الأساسي: {DEV_USERNAME}\n"
            f"• قناة السورس الرسمية: {CHANNEL_USERNAME}"
        )
        await msg.reply_text(devs_info, parse_mode="Markdown")
        return
        
    elif text in ["ID", "ايدي", "الأيدي", "معلوماتي"]:
        await msg.reply_text(
            f"👤 معلوماتك الشخصية:\n"
            f"• الاسم: {user.first_name}\n"
            f"• الأيدي (ID): `{user.id}`\n"
            f"• قناة السورس: {CHANNEL_USERNAME}",
            parse_mode="Markdown"
        )
        return

    # 3. إدارة الردود التلقائية
    if text.startswith("اضف رد "):
        try:
            parts = text.replace("اضف رد ", "").split("//")
            if len(parts) == 2:
                keyword = parts[0].strip()
                reply_val = parts[1].strip()
                custom_replies[keyword] = reply_val
                await msg.reply_text(f"✅ تم إضافة الرد للكلمة: `{keyword}` بنجاح!", parse_mode="Markdown")
            else:
                await msg.reply_text("⚠️ الصيغة خاطئة. استعمل:\n`اضف رد الكلمة // الرد`", parse_mode="Markdown")
        except Exception:
            await msg.reply_text("❌ حدث خطأ أثناء إضافة الرد.")
        return

    elif text.startswith("حذف رد "):
        keyword = text.replace("حذف رد ", "").strip()
        if keyword in custom_replies:
            del custom_replies[keyword]
            await msg.reply_text(f"🗑️ تم حذف الرد للكلمة: `{keyword}` بنجاح!", parse_mode="Markdown")
        else:
            await msg.reply_text("⚠️ هذه الكلمة غير مسجلة في قائمة الردود.")
        return

    # 4. إدارة الأوامر المخصصة
    if text.startswith("اضف امر "):
        try:
            parts = text.replace("اضف امر ", "").split("//")
            if len(parts) == 2:
                cmd_key = parts[0].strip()
                cmd_val = parts[1].strip()
                custom_commands[cmd_key] = cmd_val
                await msg.reply_text(f"✅ تم إضافة الأمر `{cmd_key}` بنجاح!", parse_mode="Markdown")
            else:
                await msg.reply_text("⚠️ الصيغة خاطئة. استعمل:\n`اضف امر الاسم // الرد`", parse_mode="Markdown")
        except Exception:
            await msg.reply_text("❌ حدث خطأ أثناء إضافة الأمر.")
        return

    elif text.startswith("حذف امر "):
        cmd_key = text.replace("حذف امر ", "").strip()
        if cmd_key in custom_commands:
            del custom_commands[cmd_key]
            await msg.reply_text(f"🗑️ تم حذف الأمر `{cmd_key}` بنجاح!", parse_mode="Markdown")
        else:
            await msg.reply_text("⚠️ هذا الأمر غير موجود.")
        return

    # 5. الفحص التلقائي للمخزن
    if text in custom_replies:
        await msg.reply_text(custom_replies[text])
        return

    if text in custom_commands:
        await msg.reply_text(custom_commands[text])
        return

def main():
    if not TOKEN:
        logger.error("لم يتم العثور على التوكن!")
        return

    application = Application.builder().token(TOKEN).build()

    # الأوامر والأزرار
    application.add_handler(CommandHandler(["start", "cmds"], start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    logger.info("🤖 تم تشغيل بوت Tb Source بكافة مميزات لوحة المطور بنجاح...")
    application.run_polling()

if __name__ == "__main__":
    main()
