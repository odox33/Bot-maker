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

# قواميس التخزين المؤقت للردود والأوامر والمميزات
custom_replies = {}  
custom_commands = {} 

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الواجهة الأساسية والمرتبة لـ Tb Source"""
    text = (
        "🤖 **مرحباً بك في لوحة تحكم Tb Source الشاملة**\n\n"
        "📂 **قائمة الأوامر والخدمات:**\n"
        "1️⃣ `/start` أو `اوامر` - عرض لوحة الأوامر الرئيسية\n"
        "2️⃣ `الرابط` أو `رابط` - جلب رابط المجموعة الفوري\n"
        "3️⃣ `المنشئين` - عرض قائمة المنشئين الأساسيين\n"
        "4️⃣ `ايدي` أو `ID` - معرفة معلوماتك والأيدي الخاص بك\n"
        "5️⃣ `ألعاب` - الدخول لقسم الألعاب والترفيه\n"
        "6️⃣ `اضف رد [الكلمة] // [الرد]` - إضافة رد تلقائي جديد\n"
        "7️⃣ `حذف رد [الكلمة]` - حذف رد تلقائي\n"
        "• `اضف امر [الامر] // [الرد]` - إضافة أمر مخصص\n"
        "• `حذف امر [الامر]` - حذف أمر مخصص\n\n"
        "🛡️ *الحماية اللانهائية والترحيب بالمنضمين مفعلة تلقائياً.*"
    )
    
    keyboard = [
        [InlineKeyboardButton("👑 لوحة المطور وصنع البوتات", callback_data="dev_panel")],
        [InlineKeyboardButton("🎮 قسم الألعاب والترفيه", callback_data="games_section")],
        [InlineKeyboardButton("📢 قناة سورس تي بي (Tb Source)", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إدارة الأزرار الشفافة واللوحات الداخلية"""
    query = update.callback_query
    await query.answer()

    if query.data == "dev_panel":
        dev_text = (
            "🛠 **لوحة مطور سورس تي بي (Tb Source)**\n\n"
            "اختر نوع الخدمة التي ترغب بها:\n\n"
            "🤖 **1. صنع بوت مجاني:**\n"
            "• يستطيع المستخدم إنشاء بوت خاص به مجاناً.\n"
            f"• **ملاحظة:** يتم وضع حقوق سورس تي بي وقناتنا ({CHANNEL_USERNAME}) تلقائياً.\n"
            f"• للاستفسار: {DEV_USERNAME}\n\n"
            "💎 **2. صنع بوت مدفوع (بدون حقوق):**\n"
            "• بوت احترافي متكامل وخالٍ من الحقوق تماماً.\n"
            f"• تتطلب هذه الخدمة مراسلتي حصراً لتنفيذها: [اضغط هنا لمراسلة المطور](https://t.me/{DEV_USERNAME.replace('@', '')})"
        )
        
        keyboard = [
            [InlineKeyboardButton("🤖 صنع بوت مجاني (مع الحقوق)", callback_data="free_bot")],
            [InlineKeyboardButton("💎 صنع بوت مدفوع (بدون حقوق)", callback_data="paid_bot")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(dev_text, parse_mode="Markdown", reply_markup=reply_markup, disable_web_page_preview=True)

    elif query.data == "games_section":
        games_text = (
            "🎮 **قسم الألعاب والترفيه في سورس تي بي:**\n\n"
            "• 🎯 لعبة الحظ السريع\n"
            "• 🧠 لعبة أسئلة الذكاء\n"
            "• ⚔️ لعبة التحدي والصراحة\n\n"
            "💡 *اختر اللعبة وابدأ التسلية مع أصدقائك في المجموعة!*"
        )
        keyboard = [
            [InlineKeyboardButton("🎯 لعبة الحظ", callback_data="game_luck"), InlineKeyboardButton("🧠 أسئلة ذكاء", callback_data="game_quiz")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(games_text, parse_mode="Markdown", reply_markup=reply_markup)

    elif query.data == "game_luck":
        await query.answer("🎲 حظك اليوم: رائع جداً، ستكون موفقاً في كل خطواتك اليوم! ✨", show_alert=True)
    elif query.data == "game_quiz":
        await query.answer("🧠 سؤال: ما هو الشيء الذي يبكي بلا عيون؟ (المطر) 🌧️", show_alert=True)

    elif query.data == "free_bot":
        await query.message.reply_text(
            f"🤖 **قسم صنع البوتات المجانية:**\n\n"
            f"أرسل توكن BotFather الخاص بك مع إبقاء حقوق سورس تي بي ({CHANNEL_USERNAME}).\n"
            f"للمساعدة راسل المطور: {DEV_USERNAME}",
            parse_mode="Markdown"
        )

    elif query.data == "paid_bot":
        await query.message.reply_text(
            f"💎 **قسم صنع البوتات المدفوعة:**\n\n"
            f"البوتات المدفوعة **بدون حقوق تماماً**. لطلب بوتك، راسلني حصراً عبر المعرف: {DEV_USERNAME}",
            parse_mode="Markdown"
        )

    elif query.data == "back_home":
        text = (
            "🤖 **مرحباً بك في لوحة تحكم Tb Source الشاملة**\n\n"
            "📂 **قائمة الأوامر والخدمات:**\n"
            "1️⃣ `/start` أو `اوامر` - عرض لوحة الأوامر الرئيسية\n"
            "2️⃣ `الرابط` - جلب رابط المجموعة الفوري\n"
            "3️⃣ `المنشئين` - عرض قائمة المنشئين الأساسيين\n"
            "4️⃣ `ايدي` - معرفة معلوماتك الشخصية\n"
            "5️⃣ `ألعاب` - قسم التسلية والترفيه"
        )
        keyboard = [
            [InlineKeyboardButton("👑 لوحة المطور وصنع البوتات", callback_data="dev_panel")],
            [InlineKeyboardButton("🎮 قسم الألعاب والترفيه", callback_data="games_section")],
            [InlineKeyboardButton("📢 قناة سورس تي بي (Tb Source)", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل، الحماية اللانهائية، الردود، والترحيب"""
    
    # 1. نظام الترحيب بالأعضاء الجدد تلقائياً عند انضمامهم للجروب
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            welcome_text = (
                f"✨ **أهلاً بك يا [{member.first_name}](tg://user?id={member.id}) في المجموعه!**\n"
                f"🌹 منورنا يا غالي، نتمنى لك أوقات ممتعة.\n"
                f"📢 تابعنا في قناة السورس: {CHANNEL_USERNAME}"
            )
            await update.message.reply_text(welcome_text, parse_mode="Markdown")
        return

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    chat = update.message.chat
    user = update.message.from_user
    msg = update.message

    # 2. نظام الحماية اللانهائية (منع الروابط وتليجرام والسبام في المجموعات لغير الإداريين)
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

    # 3. الأوامر الأساسية
    if text in ["اوامر", "الأوامر", "الالاوامر", "أوامر", "الاوامر"]:
        await start_command(update, context)
        return
        
    elif text in ["ألعاب", "العاب", "الالعاب"]:
        await msg.reply_text("🎮 **قسم الألعاب السريعة:**\n• اختر لعبة من الأزرار الشفافة في قائمة `/start` للاستمتاع بها!", parse_mode="Markdown")
        return
        
    elif text in ["الرابط", "رابط الجروب", "رابط", "الرابط"]:
        if chat.type in ["group", "supergroup"]:
            try:
                link = await chat.export_invite_link()
                await msg.reply_text(f"🔗 **رابط المجموعة الفوري:**\n{link}")
            except Exception:
                await msg.reply_text("❌ عذراً، ليس لدي صلاحية جلب الرابط (يجب أن أكون مشرفاً في المجموعة).")
        else:
            await msg.reply_text("هذا الأمر مخصص للاستخدام داخل المجموعات فقط للحصول على الرابط!")
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

    # 4. إدارة الردود التلقائية (اضف رد // حذف رد)
    if text.startswith("اضف رد "):
        try:
            parts = text.replace("اضف رد ", "").split("//")
            if len(parts) == 2:
                keyword = parts[0].strip()
                reply_val = parts[1].strip()
                custom_replies[keyword] = reply_val
                await msg.reply_text(f"✅ تم إضافة الرد للكلمة: `{keyword}` بنجاح!", parse_mode="Markdown")
            else:
                await msg.reply_text("⚠️ صيغة خاطئة. استعمل:\n`اضف رد الكلمة // الرد`", parse_mode="Markdown")
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

    # 5. إدارة الأوامر المخصصة (اضف امر // حذف امر)
    if text.startswith("اضف امر "):
        try:
            parts = text.replace("اضف امر ", "").split("//")
            if len(parts) == 2:
                cmd_key = parts[0].strip()
                cmd_val = parts[1].strip()
                custom_commands[cmd_key] = cmd_val
                await msg.reply_text(f"✅ تم إضافة الأمر `{cmd_key}` بنجاح!", parse_mode="Markdown")
            else:
                await msg.reply_text("⚠️ صيغة خاطئة. استعمل:\n`اضف امر الاسم // الرد`", parse_mode="Markdown")
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

    # 6. الفحص التلقائي للمخزن
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

    application.add_handler(CommandHandler(["start", "cmds"], start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    # معالج الرسائل يشمل النصوص وأحداث انضمام الأعضاء للترحيب والحماية
    application.add_handler(MessageHandler(filters.TEXT | filters.StatusUpdate.NEW_CHAT_MEMBERS & ~filters.COMMAND, handle_messages))

    logger.info("🤖 تم تشغيل بوت Tb Source بكافة المميزات والحماية اللانهائية بنجاح...")
    application.run_polling()

if __name__ == "__main__":
    main()
