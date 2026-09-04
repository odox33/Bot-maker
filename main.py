import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# إعداد السيرفر الوهمي لإرضاء رندر وتشغيل البوت مجاناً
app = Flask('')

@app.route('/')
def home():
    return "Source TP is running alive!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# إعدادات السورس (نفس سورس ماريو بالضبط)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_NAME = "Source TP"
BOT_USERNAME = "@odox6"

# أمر البداية (Start) بنفس أزرار وشكل سورس ماريو
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
        f"• أسرع بوت حماية مجموعات مطور خصيصاً ليكون البديل الأقوى.\n"
        f"• اضف البوت إلى مجموعتك وارفعه مشرفاً لتبدأ الحماية فوراً!"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# أمر الأيدي المتقدم
async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    text = (
        f"• مـعـلـومـاتـك الشخصية :\n\n"
        f"• الايدي : `{user.id}`\n"
        f"• المعرف : @{user.username if user.username else 'لا يوجد'}\n"
        f"• الاسم : {user.first_name}\n\n"
        f"• معلومات السورس : {BOT_NAME} ({BOT_USERNAME})\n"
        f"• ايدي الدردشة : `{chat.id}`"
    )
    
    await update.message.reply_text(text, parse_mode="Markdown")

# لوحة المطور
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("• إحصائيات Source TP •", callback_data="admin_stats")],
        [InlineKeyboardButton("• قسم الإذاعة •", callback_data="admin_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"أهلاً بك في لوحة تحكم {BOT_NAME} الأساسية ⚡️\nاختر أحد الخيارات أدناه:"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "admin_stats":
        await query.edit_message_text(f"• حالة السورس: يعمل بوت {BOT_NAME} بكفاءة عالية وبدون أي مشاكل 🚀")
    elif query.data == "admin_broadcast":
        await query.edit_message_text("• أرسل النص أو الرسالة التي تريد إذاعتها للمستخدمين.")

def main():
    # تشغيل السيرفر الوهمي في الخلفية
    keep_alive()
    
    BOT_TOKEN = os.getenv("BOT_TOKEN", "ضع_التوكن_هنا")
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
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
