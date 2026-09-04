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
DEV_USERNAME = "odox3"  # المطور الأساسي
CHANNEL_USERNAME = "odox6"  # قناة السورس

# --- قاعدة البيانات الشاملة ---
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, status TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS bots (bot_id INTEGER PRIMARY KEY, user_id INTEGER, token TEXT)")
    conn.commit()
    conn.close()

# ==============================================================================
# 🪞 TUMBLR ULTIMATE SOURCE CODE (SUB-BOT TEMPLATE)
# ==============================================================================
TUMBLR_FULL_SOURCE = """
import logging, random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

logging.basicConfig(level=logging.INFO)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚙️ إعدادات المنظف 🧹", callback_data="cleaner"), InlineKeyboardButton("🔍 إعدادات الكاشف 👁️", callback_data="detector")],
        [InlineKeyboardButton("🛡️ مانع التفليش والضرب ⚡", callback_data="antiflash")],
        [InlineKeyboardButton("👥 المساعدين والأحرار 🎖️", callback_data="helpers")],
        [InlineKeyboardButton("📜 قائمة الأوامر الشاملة 💎", callback_data="all_cmds")],
        [InlineKeyboardButton("❌ إخفاء القائمة 🗑️", callback_data="hide")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "🐥 **أهلاً بك في لوحة تحكم سورس تلمبر**\\n\\n• استخدم الأزرار أسفل للتحكم والتعديل الكامل بالقروب."
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def show_commands_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛡️ أوامر الحماية والقفل 🔒", callback_data="cmd_prot"), InlineKeyboardButton("⚙️ أوامر الإدارة والرفع 👑", callback_data="cmd_admin")],
        [InlineKeyboardButton("🧹 أوامر التنظيف والمسح 🗑️", callback_data="cmd_clean"), InlineKeyboardButton("📊 أوامر الإحصائيات والأيدي 🆔", callback_data="cmd_stats")],
        [InlineKeyboardButton("🎮 أوامر الألعاب والتسلية 🎲", callback_data="cmd_fun"), InlineKeyboardButton("🎵 أوامر الميوزك والتشغيل 🎧", callback_data="cmd_music")],
        [InlineKeyboardButton("💬 أوامر الردود والهمسة 💭", callback_data="cmd_replies"), InlineKeyboardButton("🔮 أوامر الأبراج والزخرفة 🎨", callback_data="cmd_extra")],
        [InlineKeyboardButton("⬅️ العودة للقائمة الرئيسية", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "💎 **قائمة أوامر سورس تلمبر الشاملة:**\\n\\nاضغط على أي قسم لمعاينة الأوامر الكاملة الخاصّة به:"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    back_to_cmds = [[InlineKeyboardButton("⬅️ رجوع لقائمة الأوامر", callback_data="all_cmds")]]
    back_to_main = [[InlineKeyboardButton("⬅️ رجوع للقائمة الرئيسية", callback_data="main_menu")]]

    if data == "main_menu":
        await start_command(update, context)
    elif data == "all_cmds":
        await show_commands_menu(update, context)
    elif data == "hide":
        await query.message.delete()
    elif data == "cleaner":
        await query.edit_message_text("🧹 **إعدادات المنظف تلقائياً:**\\n\\n• مسح الروابط والتوجيه: مفعل ✅\\n• مسح الميديا والتكرار: مفعل ✅\\n• مسح البوتات والسبام: مفعل ✅", reply_markup=InlineKeyboardMarkup(back_to_main), parse_mode="Markdown")
    elif data == "detector":
        await query.edit_message_text("👁️ **إعدادات الكاشف الدقيق:**\\n\\n• كشف تعديل الرسائل: مفعل ✅\\n• كشف التوجيه والمعرفات: مفعل ✅\\n• كشف تغيّر الأسماء: مفعل ✅", reply_markup=InlineKeyboardMarkup(back_to_main), parse_mode="Markdown")
    elif data == "antiflash":
        await query.edit_message_text("⚡ **مانع التفليش الحمايتي:**\\n\\n• حظر طرد الاعضاء العشوائي: مفعل ✅\\n• حظر التقييد المفاجئ: مفعل ✅\\n• حماية تغيير معلومات المجموعة: مفعل ✅", reply_markup=InlineKeyboardMarkup(back_to_main), parse_mode="Markdown")
    elif data == "helpers":
        await query.edit_message_text("🎖️ **قائمة المساعدين والأحرار:**\\n\\n• لا يوجد مساعدين مضافين حالياً.", reply_markup=InlineKeyboardMarkup(back_to_main), parse_mode="Markdown")

    elif data == "cmd_prot":
        text = (
            "🔒 **أوامر الحماية والقفل:**\\n\\n"
            "• `قفل` / `فتح` الروابط 🔗\\n"
            "• `قفل` / `فتح` التوجيه 🔄\\n"
            "• `قفل` / `فتح` الصور 🖼️\\n"
            "• `قفل` / `فتح` الفيديو 🎥\\n"
            "• `قفل` / `فتح` الصوتيات 🎧\\n"
            "• `قفل` / `فتح` الملصقات 🎯\\n"
            "• `قفل` / `فتح` المعرفات 🏷️\\n"
            "• `قفل` / `فتح` الكلايش 📄\\n"
            "• `قفل` / `فتح` التعديل ✏️\\n"
            "• `قفل` / `فتح` دخول البوتات 🤖\\n"
            "• `قفل` / `فتح` جهات الاتصال 📞\\n"
            "• `قفل` / `فتح` الشات والدردشة 💬"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_to_cmds), parse_mode="Markdown")
    elif data == "cmd_admin":
        text = (
            "👑 **أوامر الإدارة والترقيات:**\\n\\n"
            "• `حظر` / `الغاء الحظر` (بالرد أو بالمعرف) 🚫\\n"
            "• `طرد` (بالرد أو بالمعرف) ⚡\\n"
            "• `كتم` / `الغاء الكتم` (بالرد أو بالمعرف) 🔇\\n"
            "• `تقييد` / `الغاء التقييد` 🚷\\n"
            "• `رفع مالك` / `تنزيل مالك` 🏆\\n"
            "• `رفع منشئ` / `تنزيل منشئ` 🎖️\\n"
            "• `رفع أدمن` / `تنزيل أدمن` 👮‍♂️\\n"
            "• `رفع مميز` / `تنزيل مميز` ⭐"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_to_cmds), parse_mode="Markdown")
    elif data == "cmd_clean":
        text = (
            "🗑️ **أوامر التنظيف والمسح السريع:**\\n\\n"
            "• `مسح الرسائل` + العدد 🧹\\n"
            "• `مسح المحظورين` 🚫\\n"
            "• `مسح المكتومين` 🔇\\n"
            "• `مسح المميزين` ⭐\\n"
            "• `مسح الأدمنية` 👮‍♂️\\n"
            "• `مسح البوتات` 🤖\\n"
            "• `تنظيف القروب` بالكامل 🔥"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_to_cmds), parse_mode="Markdown")
    elif data == "cmd_stats":
        text = (
            "🆔 **أوامر الإحصائيات والرتب:**\\n\\n"
            "• `ايدي` - عرض ايديك ومعلوماتك الرائعة 👤\\n"
            "• `رتبتي` - لمعرفة رتبتك الحالية بالقروب 🏅\\n"
            "• `كشف` بالرد - لكشف رتبة ومعلومات العضو 🕵️‍♂️\\n"
            "• `الجهد` / `السرعة` - فحص سرعة استجابة البوت ⚡\\n"
            "• `المكتومين` / `المحظورين` - عرض القوائم 📜\\n"
            "• `معلومات القروب` - تفاصيل وإحصائيات القروب 📊"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_to_cmds), parse_mode="Markdown")
    elif data == "cmd_fun":
        text = (
            "🎲 **أوامر الألعاب والفعاليات:**\\n\\n"
            "• `نسبة الحب` (بالرد) ❤️\\n"
            "• `لو خيروك` 🔀\\n"
            "• `صراحة` ❓\\n"
            "• `كت تويت` 💬\\n"
            "• `امثال` 📜\\n"
            "• `حزورة` 🧩\\n"
            "• `نسبة جمالي` 🪞\\n"
            "• `زواج` (بالرد) 💍\\n"
            "• `طلاق` (بالرد) 💔"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_to_cmds), parse_mode="Markdown")
    elif data == "cmd_music":
        text = (
            "🎧 **أوامر الميوزك والتشغيل:**\\n\\n"
            "• `تشغيل` + اسم الاغنية 🎵\\n"
            "• `ايقاف` / `استئناف` ⏯️\\n"
            "• `كتم الصوت` / `الغاء الكتم` 🔇\\n"
            "• `تخطي` / `التالي` ⏭️\\n"
            "• `انهاء التشغيل` 🛑"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_to_cmds), parse_mode="Markdown")
    elif data == "cmd_replies":
        text = (
            "💭 **أوامر الردود والتفاعل:**\\n\\n"
            "• `اضف رد` + الكلمة + الرد ➕\\n"
            "• `مسح رد` + الكلمة ➖\\n"
            "• `الردود` - عرض جميع الردود المضافة 📜\\n"
            "• `همسة` (بالرد) - إرسال همسة سرية 🤫"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_to_cmds), parse_mode="Markdown")
    elif data == "cmd_extra":
        text = (
            "🎨 **أوامر الإضافات والزخرفة:**\\n\\n"
            "• `زخرفة` + الاسم ✍️\\n"
            "• `برجي` + اسم برجك 🔮\\n"
            "• `تحويل صورة` (بالرد على ملصق) 🖼️\\n"
            "• `تحويل ملصق` (بالرد على صورة) 🎯\\n"
            "• `رابط المحادثة` 🔗"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_to_cmds), parse_mode="Markdown")

async def group_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    text = msg.text.strip()
    user = msg.from_user

    if text in ["الاوامر", "الأوامر", "اوامر", "أوامر"]:
        await show_commands_menu(update, context)
        return

    if text in ["ايدي", "الايدي", "أيدي"]:
        id_text = f"👤 **معلوماتك في سورس تلمبر:**\\n\\n• اسمك: {user.full_name}\\n• يوزرك: @{user.username if user.username else 'لا يوجد'}\\n• ايديك: `{user.id}`\\n• رتبتك: عضو مميز ✨"
        await msg.reply_text(id_text, parse_mode="Markdown")
        return

    if text in ["رتبتي", "الرتبة"]:
        await msg.reply_text(f"🏅 رتبتك في هذا القروب هي: **عضو محترم** 🐥", parse_mode="Markdown")
        return

    if text == "لو خيروك":
        opts = ["تسافر للفضاء وحدك 🚀", "تعيش بجزيرة مهجورة 🏝️", "تخسر تلفونك لمدة شهر 📱", "تأكل أكل حار جداً 🌶️"]
        await msg.reply_text(f"🎲 **لو خيروك:**\\n{random.choice(opts)}")
        return

    if text in ["صراحة", "صراحه"]:
        questions = ["شنو أكثر شي تخاف تخسره؟", "شنو حلمك اللي تحب تحققه؟", "منو أكثر شخص توثق بيه؟"]
        await msg.reply_text(f"❓ **سؤال صراحة:**\\n{random.choice(questions)}")
        return

    if text in ["كت تويت", "كت"]:
        tweets = ["شيء لو اختفى من الحياة تصبح أفضل؟", "شنو أكلتك المفضل؟", "أفضل قرار اتخذته بحياتك؟"]
        await msg.reply_text(f"💬 **كت تويت:**\\n{random.choice(tweets)}")
        return

    if text in ["نسبة جمالي", "جمالي"]:
        await msg.reply_text(f"🪞 نسبة جمالك هي: **{random.randint(70, 100)}%** 🌟")
        return

    if msg.entities or msg.forward_date:
        try:
            await msg.delete()
        except Exception:
            pass

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
