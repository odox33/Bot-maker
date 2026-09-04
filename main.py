import os
import logging
import sqlite3
import random
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8704690798:AAEzN1NuoDVAoaqo3lW4-Oxb2IBeSy-DNrs"
DEV_USERNAME = "odox3"
CHANNEL_USERNAME = "odox6"

def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS bots (bot_id INTEGER PRIMARY KEY, user_id INTEGER, token TEXT)")
    conn.commit()
    conn.close()

# ==============================================================================
# 🪞 TUMBLR SOURCE CODE (NEW NUMERICAL MENU STYLE)
# ==============================================================================
TUMBLR_FULL_SOURCE = """
import logging, random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)

# --- 🎯 NUMERICAL COMMANDS MENU ---

async def show_commands_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("• 1 •", callback_data="m1"), InlineKeyboardButton("• 2 •", callback_data="m2")],
        [InlineKeyboardButton("• 3 •", callback_data="m3")],
        [InlineKeyboardButton("• 4 •", callback_data="m4"), InlineKeyboardButton("• 5 •", callback_data="m5")],
        [InlineKeyboardButton("• 6 •", callback_data="m6")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "- : اليك اوامر البوت ⚡⚡.\\n\\n"
        "- : { م1 } ~ اوامر الحمايه\\n"
        "- : { م2 } ~ اوامر المشرفين\\n"
        "- : { م3 } ~ اوامر التفعيلات\\n"
        "- : { م4 } ~ اوامر المسح\\n"
        "- : { م5 } ~ اوامر المطورين\\n"
        "- : { م6 } ~ اوامر الترفيه"
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚙️ إعدادات المنظف 🧹", callback_data="cleaner"), InlineKeyboardButton("🔍 إعدادات الكاشف 👁️", callback_data="detector")],
        [InlineKeyboardButton("📜 قائمة الأوامر 💎", callback_data="all_cmds")],
        [InlineKeyboardButton("❌ إخفاء 🗑️", callback_data="hide")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🐥 **أهلاً بك في سورس تلمبر**\\n\\nارسل كلمة `الاوامر` أو استخدم الأزرار بالأسفل."
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# --- 🔘 BUTTON ROUTER ---

async def button_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ رجوع", callback_data="all_cmds")]])

    if data == "all_cmds":
        await show_commands_menu(update, context)
    elif data == "hide":
        await query.message.delete()
    
    # --- NUMERICAL SECTIONS ---
    elif data == "m1":
        text = (
            "🔒 **( م1 ) ~ أوامر الحماية والقفل:**\\n\\n"
            "• قفل / فتح (الروابط - التوجيه - الصور - الفيديو - الصوتيات - الملصقات - المعرفات - الكلايش - التعديل - البوتات - الشات)"
        )
        await query.edit_message_text(text, reply_markup=back_btn, parse_mode="Markdown")
    elif data == "m2":
        text = (
            "👑 **( م2 ) ~ أوامر المشرفين والإدارة:**\\n\\n"
            "• حظر / الغاء الحظر (بالرد أو المعرف)\\n"
            "• طرد (بالرد أو المعرف)\\n"
            "• كتم / الغاء الكتم (بالرد أو المعرف)\\n"
            "• تقييد / الغاء التقييد\\n"
            "• رفع أدمن / تنزيل أدمن\\n"
            "• رفع مميز / تنزيل مميز"
        )
        await query.edit_message_text(text, reply_markup=back_btn, parse_mode="Markdown")
    elif data == "m3":
        text = (
            "⚙️ **( م3 ) ~ أوامر التفعيلات والتعطيل:**\\n\\n"
            "• تفعيل / تعطيل الحماية\\n"
            "• تفعيل / تعطيل الترحيب\\n"
            "• تفعيل / تعطيل الردود\\n"
            "• تفعيل / تعطيل الألعاب\\n"
            "• تفعيل / تعطيل الميديا"
        )
        await query.edit_message_text(text, reply_markup=back_btn, parse_mode="Markdown")
    elif data == "m4":
        text = (
            "🗑️ **( م4 ) ~ أوامر المسح والتنظيف:**\\n\\n"
            "• مسح الرسائل + العدد\\n"
            "• مسح المحظورين\\n"
            "• مسح المكتومين\\n"
            "• مسح المميزين\\n"
            "• مسح الأدمنية\\n"
            "• مسح البوتات"
        )
        await query.edit_message_text(text, reply_markup=back_btn, parse_mode="Markdown")
    elif data == "m5":
        text = (
            "👨‍💻 **( م5 ) ~ أوامر المطورين:**\\n\\n"
            "• رفع مطور / تنزيل مطور\\n"
            "• قائمة المطورين\\n"
            "• إذاعة (لكل القروبات / الخاص)\\n"
            "• الإحصائيات الشاملة\\n"
            "• مغادرة قروب معين"
        )
        await query.edit_message_text(text, reply_markup=back_btn, parse_mode="Markdown")
    elif data == "m6":
        text = (
            "🎲 **( م6 ) ~ أوامر الترفيه والفعاليات:**\\n\\n"
            "• ايدي / رتبتي / نسبة الحب\\n"
            "• لو خيروك / صراحة / كت تويت\\n"
            "• امثال / حزورة / نسبة جمالي\\n"
            "• زواج / طلاق (بالرد)\\n"
            "• تشغيل / ايقاف (ميوزك)"
        )
        await query.edit_message_text(text, reply_markup=back_btn, parse_mode="Markdown")

# --- 💬 TEXT HANDLER ---

async def group_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    text = msg.text.strip()
    user = msg.from_user

    if text in ["الاوامر", "الأوامر", "اوامر", "أوامر"]:
        await show_commands_menu(update, context)
        return

    if text in ["ايدي", "الايدي"]:
        id_text = f"👤 **معلوماتك:**\\n\\n• الاسم: {user.full_name}\\n• اليوزر: @{user.username if user.username else 'لا يوجد'}\\n• الايدي: `{user.id}`"
        await msg.reply_text(id_text, parse_mode="Markdown")
        return

    if text == "لو خيروك":
        opts = ["تسافر للفضاء وحدك 🚀", "تعيش بجزيرة مهجورة 🏝️", "تخسر تلفونك لمدة شهر 📱"]
        await msg.reply_text(f"🎲 **لو خيروك:**\\n{random.choice(opts)}")
        return

    if text in ["صراحة", "صراحه"]:
        questions = ["شنو أكثر شي تخاف تخسره؟", "شنو حلمك اللي تحب تحققه؟"]
        await msg.reply_text(f"❓ **سؤال صراحة:**\\n{random.choice(questions)}")
        return

def main():
    app = Application.builder().token("{TOKEN}").build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("cmds", show_commands_menu))
    app.add_handler(CallbackQueryHandler(button_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_text_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
"""

# ==============================================================================
# 🏭 FACTORY BOT HANDLERS
# ==============================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛠️ إنشاء بوت حماية تلمبر", callback_data="make_bot")],
        [InlineKeyboardButton("💳 طرق الاشتراك والتفعيل", callback_data="buy_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 **أهلاً بك في مصنع بوتات حماية سورس تلمبر!**\n\n"
        f"• المطور: @{DEV_USERNAME}\n"
        f"• القناة: @{CHANNEL_USERNAME}\n\n"
        "اضغط على الزر أدناه للبدء بإنشاء بوتك الخاص:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "make_bot":
        await query.edit_message_text("أرسل الآن **توكن البوت** الخاص بك من @BotFather:")
    elif query.data == "buy_info":
        await query.edit_message_text("أسعار الاشتراكات:\n- تجربة 3 أيام: مجاناً\n- اشتراك شهري: 5$")

async def handle_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    token = update.message.text.strip()
    user_id = update.effective_user.id
    if ":" not in token or len(token) < 30:
        await update.message.reply_text("❌ التوكن غير صحيح! أرسل توكن صحيح من BotFather.")
        return
    await update.message.reply_text("⏳ جاري تنصيب وتجهيز البوت بالأوامر الجديدة...")
    filename = f"bot_{user_id}.py"
    with open(filename, "w") as f:
        f.write(TUMBLR_FULL_SOURCE.replace("{TOKEN}", token))
    subprocess.Popen(["python3", filename])
    await update.message.reply_text("✅ **تم تشغيل بوت الحماية بنجاح!**\n\nأضف البوت لمجموعتك ورفعه مشرفاً، ثم أرسل كلمة `الاوامر` داخل القروب!")

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_token))
    app.run_polling()

if __name__ == "__main__":
    main()
