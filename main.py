import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# إعداد السجلات لمتابعة حالة البوت
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# قراءة التوكن من متغيرات البيئة مع التوكن الخاص بك احتياطياً
TOKEN = os.environ.get("BOT_TOKEN", "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w")

# قواميس التخزين المؤقت للردود والأوامر المخصصة
custom_replies = {}  # { "الكلمة": "الرد" }
custom_commands = {} # { "الأمر": "رد الأمر" }

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الواجهة والأوامر الأساسية لـ Tb Source"""
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
        "• `حذف امر [الامر]` - حذف أمر مخصص\n"
        "🛡️ *ميزة الحماية مفعلة تلقائياً (منع الروابط في المجموعات)*"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل، الحماية، الأوامر الأساسية، وإدارة الإضافات"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    chat = update.message.chat
    user = update.message.from_user
    msg = update.message

    # 1. نظام حماية المجموعات المتقدم (منع نشر الروابط والتليجرام لغير المشرفين)
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

    # 2. الأوامر الأساسية والواجهات
    if text in ["اوامر", "الأوامر", "الالاوامر", "أوامر", "الاوامر"]:
        await start_command(update, context)
        return
        
    elif text in ["الرابط", "رابط الجروب", "رابط"]:
        if chat.type in ["group", "supergroup"]:
            try:
                link = await chat.export_invite_link()
                await msg.reply_text(f"🔗 رابط المجموعة:\n{link}")
            except Exception:
                await msg.reply_text("❌ عذراً، ليس لدي صلاحية جلب الرابط (يجب أن أكون مشرفاً في المجموعة).")
        else:
            await msg.reply_text("هذا الأمر مخصص للاستخدام داخل المجموعات فقط!")
        return
        
    elif text in ["المنشئين", "المنشئين الاساسيين", "المطور", "المطورين"]:
        devs_info = (
            "👑 **قائمة المنشئين الأساسيين لـ Tb Source:**\n"
            "• المطور الرئيسي والمسؤول عن السورس.\n"
            "💡 *البوت يعمل بأعلى كفاءة وأمان تام.*"
        )
        await msg.reply_text(devs_info, parse_mode="Markdown")
        return
        
    elif text in ["ID", "ايدي", "الأيدي", "معلوماتي"]:
        await msg.reply_text(
            f"👤 معلوماتك الشخصية:\n"
            f"• الاسم: {user.first_name}\n"
            f"• الأيدي (ID): `{user.id}`\n"
            f"• معرف المستخدم: @{user.username if user.username else 'لا يوجد'}",
            parse_mode="Markdown"
        )
        return

    # 3. نظام إدارة الردود التلقائية (اضف رد // حذف رد)
    if text.startswith("اضف رد "):
        try:
            parts = text.replace("اضف رد ", "").split("//")
            if len(parts) == 2:
                keyword = parts[0].strip()
                reply_val = parts[1].strip()
                custom_replies[keyword] = reply_val
                await msg.reply_text(f"✅ تم إضافة الرد للكلمة: `{keyword}` بنجاح!", parse_mode="Markdown")
            else:
                await msg.reply_text("⚠️ صيغة خاطئة. استعمل الطريقة الآتية:\n`اضف رد الكلمة // الرد المطلوب`", parse_mode="Markdown")
        except Exception:
            await msg.reply_text("❌ حدث خطأ أثناء إضافة الرد.")
        return

    elif text.startswith("حذف رد "):
        keyword = text.replace("حذف رد ", "").strip()
        if keyword in custom_replies:
            del custom_replies[keyword]
            await msg.reply_text(f"🗑️ تم حذف الرد للكلمة: `{keyword}` بنجاح!", parse_mode="Markdown")
        else:
            await msg.reply_text("⚠️ هذه الكلمة غير مسجلة في قائمة الردود التلقائية.")
        return

    # 4. نظام إدارة الأوامر المخصصة (اضف امر // حذف امر)
    if text.startswith("اضف امر "):
        try:
            parts = text.replace("اضف امر ", "").split("//")
            if len(parts) == 2:
                cmd_key = parts[0].strip()
                cmd_val = parts[1].strip()
                custom_commands[cmd_key] = cmd_val
                await msg.reply_text(f"✅ تم إضافة الأمر المخصص `{cmd_key}` بنجاح!", parse_mode="Markdown")
            else:
                await msg.reply_text("⚠️ صيغة خاطئة. استعمل الطريقة الآتية:\n`اضف امر اسم_الأمر // الرد`", parse_mode="Markdown")
        except Exception:
            await msg.reply_text("❌ حدث خطأ أثناء إضافة الأمر.")
        return

    elif text.startswith("حذف امر "):
        cmd_key = text.replace("حذف امر ", "").strip()
        if cmd_key in custom_commands:
            del custom_commands[cmd_key]
            await msg.reply_text(f"🗑️ تم حذف الأمر المخصص `{cmd_key}` بنجاح!", parse_mode="Markdown")
        else:
            await msg.reply_text("⚠️ هذا الأمر غير موجود في القائمة المخصصة.")
        return

    # 5. الفحص التلقائي للردود والأوامر المخزنة مسبقاً
    if text in custom_replies:
        await msg.reply_text(custom_replies[text])
        return

    if text in custom_commands:
        await msg.reply_text(custom_commands[text])
        return

def main():
    if not TOKEN:
        logger.error("لم يتم العثور على توكن البوت!")
        return

    application = Application.builder().token(TOKEN).build()

    # تسجيل الأوامر الأساسية لنظام تيليجرام
    application.add_handler(CommandHandler(["start", "cmds"], start_command))

    # معالج الرسائل الشامل لكل الميزات والحماية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    logger.info("🤖 تم تشغيل بوت Tb Source بكافة المميزات بنجاح تام...")
    application.run_polling()

if __name__ == "__main__":
    main()
