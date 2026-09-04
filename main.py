import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# إعداد التسجيل لمتابعة حالة البوت
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# معلومات السورس والبوت الأساسية
BOT_NAME = "Source TP"
BOT_USERNAME = "@odox6"

# دالة البدء (Start) بتصميم مشابه لسورس ماريو
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("• اضف البوت لمجموعتك •", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("• قناة السورس •", url="https://t.me/odox6")],
        [InlineKeyboardButton("• المطور •", url=f"tg://user?id={user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"مرحباً بك عزيزي في بوت {BOT_NAME} 🤖\n\n"
        f"• أسرع بوت حماية مجموعات مطور خصيصاً ليكون بديل قوي وممتاز.\n"
        f"• اضف البوت إلى مجموعتك وارفعه مشرفاً لتبدأ الحماية فوراً!"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# دالة الأيدي المتقدمة (تعرض معلوماتك ومعلومات السورس بوضوح)
async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    text = (
        f"• مـعـلـومـاتـك الشخصية :\n\n"
        f"• الايدي : `{user.id}`\n"
        f"• المعرف : @{user.username if user.username else 'لا يوجد'}\n"
        f"• الاسم : {user.first_name}\n\n"
        f"• معلومات السورس : {BOT_NAME} ({BOT_USERNAME})\n"
        f"• ايدي الدردشة : `{chat.id}`\n"
        f"• نوع الدردشة : {chat.type}"
    )
    
    if chat.type in ["group", "supergroup"]:
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")

# دالة لوحة المطور الخاصة بالتحكم
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("• إحصائيات Source TP •", callback_data="admin_stats")],
        [InlineKeyboardButton("• قسم الإذاعة •", callback_data="admin_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"أهلاً بك في لوحة تحكم {BOT_NAME} الأساسية ⚡️\nاختر أحد الخيارات أدناه:"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)

# دالة معالجة الأزرار الشفافة
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "admin_stats":
        await query.edit_message_text("• حالة السورس: يعمل بوت {BOT_NAME} بكفاءة عالية وبدون أي مشاكل 🚀")
    elif query.data == "admin_broadcast":
        await query.edit_message_text("• أرسل النص أو الرسالة التي تريد إذاعتها للمستخدمين.")

def main():
    # ملاحظة: التوكن يُؤخذ تلقائياً من بيئة العمل في Render أو وضعه هنا مباشرة
    import os
    BOT_TOKEN = os.getenv("BOT_TOKEN", "ضع_التوكن_هنا_إن_لم_تستخدم_Environment_Variables")
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # ربط الأوامر (تدعم الإنجليزية والعربية)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(CommandHandler("ايدي", id_command))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("المطور", admin_panel))
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    print(f"{BOT_NAME} Bot started successfully!")
    application.run_polling()

if __name__ == "__main__":
    main()
