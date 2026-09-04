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

# قراءة التوكن من متغيرات البيئة أو وضعه مباشرة للتجربة السريعة
TOKEN = os.environ.get("BOT_TOKEN", "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w")

# قواميس التخزين المؤقت للردود والأوامر المضافة
custom_replies = {}  # { "الكلمة": "الرد الخاص بها" }
custom_commands = {} # { "الأمر": "رد الأمر المخصص" }

# قائمة المطورين الأساسيين (يمكنك تعديل الأيدي الخاص بك)
DEV_IDS = [] 

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الواجهة والأوامر الـ 7 الأساسية"""
    text = (
        "🤖 **مرحباً بك في لوحة تحكم Tb Source**\n\n"
        "إليك قائمة الأوامر والخدمات الأساسية:\n"
        "1️⃣ `/start` - عرض لوحة الأوامر الرئيسية\n"
        "2️⃣ `اوامر` - عرض لوحة الأوامر السريعة\n"
        "3️⃣ `الرابط` - جلب رابط المجموعة\n"
        "4️⃣ `المنشئين` - عرض قائمة المنشئين الأساسيين\n"
        "5️⃣ `ايدي` (أو ID) - معرفة معلوماتك الشخصية\n"
        "6️⃣ `اضف رد [الكلمة] // [الرد]` - إضافة رد تلقائي جديد\n"
        "7️⃣ `حذف رد [الكلمة]` - حذف رد تلقائي\n"
        "• `اضف امر [الامر] // [الرد]` - إضافة أمر مخصص\n"
        "• `حذف امر [الامر]` - حذف أمر مخصص"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown")

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل، الأوامر الأساسية، وإدارة الردود والأوامر المضافة"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    chat = update.message.chat
    user = update.message.from_user
    msg = update.message

    # 1. حماية المجموعات (منع الروابط)
    if chat.type in ["group", "supergroup"]:
        if "http://" in text or "https://" in text or "t.me/" in text:
            try:
                member = await chat.get_member(user.id)
                if member.status not in ["creator", "administrator"]:
                    await msg.delete()
                    await chat.send_message(
                        f"⚠️ عذراً يا [{user.first_name}](tg://user?id={user.id})، ممنوع نشر الروابط هنا!",
                        parse_mode="Markdown"
                    )
                    return
            except Exception:
                pass

    # 2. الأوامر الأساسية
    if text in ["اوامر", "الأوامر", "الالاوامر", "أوامر"]:
        await start_command(update, context)
        return
        
    elif text in ["الرابط", "رابط الجروب"]:
        if chat.type in ["group", "supergroup"]:
            try:
                link = await chat.export_invite_link()
                await msg.reply_text(f"🔗 رابط المجموعة:\n{link}")
            except Exception:
                await msg.reply_text("❌ ليس لدي صلاحية جلب الرابط (يجب أن أكون مشرفاً).")
        else:
            await msg.reply_text("هذا الأمر مخصص للمجموعات فقط!")
        return
        
    elif text in ["المنشئين", "المنشئين الاساسيين", "المطور"]:
        await msg.reply_text("👑 **قائمة المنشئين الأساسيين لـ Tb Source:**\n- المطور الأساسي للملفات والبرمجيات", parse_mode="Markdown")
        return
        
    elif text in ["ID", "ايدي", "الأيدي"]:
        await msg.reply_text(
            f"👤 معلوماتك الشخصية:\n- الاسم: {user.first_name}\n- الايدي (ID): `{user.id}`",
            parse_mode="Markdown"
        )
        return

    # 3. نظام إضافة وحذف الردود (اضف رد // حذف رد)
    if text.startswith("اضف رد "):
        try:
            parts = text.replace("اضف رد ", "").split("//")
            if len(parts) == 2:
                keyword = parts[0].strip()
                reply_text = parts[1].strip()
                custom_replies[keyword] = reply_text
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
            await msg.reply_text("⚠️ هذه الكلمة غير موجودة في قائمة الردود.")
        return

    # 4. نظام إضافة وحذف الأوامر (اضف امر // حذف امر)
    if text.startswith("اضف امر "):
        try:
            parts = text.replace("اضف امر ", "").split("//")
            if len(parts) == 2:
                cmd_name = parts[0].strip()
                cmd_reply = parts[1].strip()
                custom_commands[cmd_name] = cmd_reply
                await msg.reply_text(f"✅ تم إضافة الأمر `{cmd_name}` بنجاح!", parse_mode="Markdown")
            else:
                await msg.reply_text("⚠️ الصيغة خاطئة. استعمل:\n`اضف امر الاسم // الرد`", parse_mode="Markdown")
        except Exception:
            await msg.reply_text("❌ حدث خطأ أثناء إضافة الأمر.")
        return

    elif text.startswith("حذف امر "):
        cmd_name = text.replace("حذف امر ", "").strip()
        if cmd_name in custom_commands:
            del custom_commands[cmd_name]
            await msg.reply_text(f"🗑️ تم حذف الأمر `{cmd_name}` بنجاح!", parse_mode="Markdown")
        else:
            await msg.reply_text("⚠️ هذا الأمر غير موجود في القائمة المخصصة.")
        return

    # 5. فحص الردود والأوامر المخزنة مسبقاً والرد عليها
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

    # الأوامر النظامية الأساسية عبر CommandHandler
    application.add_handler(CommandHandler(["start", "cmds"], start_command))

    # معالج الرسائل الشامل لكل الردود، الأوامر العربية، والإضافات الديناميكية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    logger.info("🤖 تم تشغيل بوت Tb Source بنجاح تام...")
    application.run_polling()

if __name__ == "__main__":
    main()
