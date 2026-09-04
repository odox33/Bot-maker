import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

MAIN_TEXT = (
    "Tb\n"
    "الاوامر\n\n"
    "- : اليك اوامر سورس تي بي (Source TP) ⚡️⚡️\n\n"
    "- [ م 1 ] ↜ اوامر الحمايه\n"
    "- [ م 2 ] ↜ اوامر المشرفين\n"
    "- [ م 3 ] ↜ اوامر التفعيلات\n"
    "- [ م 4 ] ↜ اوامر المسح\n"
    "- [ م 5 ] ↜ اوامر المطورين\n"
    "- [ م 6 ] ↜ اوامر الترفيه"
)

MAIN_KEYBOARD = InlineKeyboardMarkup([
    [InlineKeyboardButton("• 1 •", callback_data="sec_1"), InlineKeyboardButton("• 2 •", callback_data="sec_2")],
    [InlineKeyboardButton("• 3 •", callback_data="sec_3")],
    [InlineKeyboardButton("• 4 •", callback_data="sec_4"), InlineKeyboardButton("• 5 •", callback_data="sec_5")],
    [InlineKeyboardButton("• 6 •", callback_data="sec_6")],
    [InlineKeyboardButton("قناة السورس", url="https://t.me/odox6")]
])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_text = (
        "Tb\n"
        "/start\n\n"
        "- : اهلا بك عزيزي المطور الاساسي (@odox3)\n"
        "- : اليك كيبورد أوامر سورس تي بي (Source TP)\n"
        "- : قناة السورس : @odox6\n"
        "- : نوع البوت : - مدفوع ينتهي بعد 14 يوم"
    )
    start_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("قناة التحديثات", url="https://t.me/odox6")],
        [InlineKeyboardButton("اعدادات الاساسي", callback_data="sec_basic")],
        [InlineKeyboardButton("اعدادات البوت", callback_data="sec_bot_settings"), InlineKeyboardButton("اعدادات الطلبات", callback_data="sec_requests")],
        [InlineKeyboardButton("اوامر الاشتراك الاجباري", callback_data="sec_sub")],
        [InlineKeyboardButton("اوامر الاذاعة", callback_data="sec_broadcast"), InlineKeyboardButton("الاوامر العامة", callback_data="sec_general")],
        [InlineKeyboardButton("الغاء الامر", callback_data="back_home")]
    ])
    await update.message.reply_text(start_text, reply_markup=start_keyboard)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "sec_1":
        text = "- : اوامر ( القفل والفتح ) ⚡️⚡️\n• التاك • القنوات\n• الصور • الروابط"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("• القائمه الرئيسيه •", callback_data="back_home")]])
        await query.edit_message_text(text, reply_markup=keyboard)
    elif data == "back_home":
        await query.edit_message_text(MAIN_TEXT, reply_markup=MAIN_KEYBOARD)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler(["start", "الاوامر"], start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
