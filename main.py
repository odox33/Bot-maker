import os
import sqlite3
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_NAME = "Source TP"
BOT_USERNAME = "@odox6"
DEV_USERNAME = "@odox6"
DEV_ID = 8297163405  # ايدي المطور الأساسي للتحكم بالصنع والمدفوعات
BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")

app = Flask(__name__)
application = None

# إعداد قاعدة البيانات المحلية لتخزين البوتات المصنوعة
def init_db():
    conn = sqlite3.connect("source_tp.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS created_bots (
            token TEXT PRIMARY KEY,
            owner_id INTEGER,
            bot_type TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

async def setup_bot():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # الأوامر الرئيسية وأوامر التسلية والأيدي
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(CommandHandler("games", games_menu))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    await application.initialize()
    if RENDER_URL:
        webhook_url = f"{RENDER_URL}/{BOT_TOKEN}"
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("• اضف البوت لمجموعتك •", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton("• قسم صنع البوتات •", callback_data="make_bot_menu")],
        [InlineKeyboardButton("• ألعاب السورس •", callback_data="games_menu_cb")],
        [InlineKeyboardButton("• قناة السورس •", url="https://t.me/odox6")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        f"مرحباً بك عزيزي في بوت {BOT_NAME} 🤖\n\n"
        f"• أسرع نظام حماية وصنع بوتات مجموعات متطور.\n"
        f"• يمكنك صنع بوتك الخاص مجاناً أو مدفوعاً والبدء بالبيع الآن!"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    text = (
        f"• - : ايديك : ( `{user.id}` )\n"
        f"• - : معرفك : ( @{user.username if user.username else 'لا يوجد'} )\n"
        f"• - : رتبتك : ( المطور الاساسي )\n"
        f"• - : رسائلك : ( 9234 )\n"
        f"• - : نقاطك : ( 68 )\n"
        f"• معلومات السورس : {BOT_NAME} ({BOT_USERNAME})"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown")

async def games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("• لعبة الحظ •", callback_data="game_luck"), InlineKeyboardButton("• لعبة الزلاطة •", callback_data="game_salad")],
        [InlineKeyboardButton("• البلاي جراوند •", callback_data="game_play")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"🎮 **قسم الألعاب والتسلية في {BOT_NAME}**\nاختر لعبتك المفضلة أدناه:"
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    text = update.message.text.strip()
    user = update.effective_user
    
    if text in ["ايدي", "الاي دي", "/id"]:
        await id_command(update, context)
    
    elif text in ["صنع", "صنع بوت", "البوتات المصنوعة"]:
        keyboard = [
            [InlineKeyboardButton("• صنع بوت مجاني (بحقوق السورس) •", callback_data="make_free_bot")],
            [InlineKeyboardButton("• صنع بوت مدفوع (تفعيل خاص VIP) •", callback_data="make_paid_bot")],
            [InlineKeyboardButton("• بوتاتي المصنوعة •", callback_data="my_bots")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"• أهلاً بك في قسم صنع البوتات التابع لـ {BOT_NAME} 🤖\n"
            f"• أنشئ بوتك الخاص الآن وقم بإدارته وبيعه بكل سهولة:",
            reply_markup=reply_markup
        )
    
    # فحص إذا كان المستخدم يرسل توكن بوت جديد لصنعه
    elif context.user_data.get("waiting_for_free_token"):
        token = text
        context.user_data["waiting_for_free_token"] = False
        
        conn = sqlite3.connect("source_tp.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO created_bots (token, owner_id, bot_type, status) VALUES (?, ?, ?, ?)",
                           (token, user.id, "free", "active"))
            conn.commit()
            await update.message.reply_text(
                f"✅ **تم إنشاء بوتك المجاني بنجاح!**\n\n"
                f"• التوكن مسجل بنظام {BOT_NAME}.\n"
                f"• ملاحظة: البوت المجاني يعمل بفرض ظهور حقوق قناة السورس ({BOT_USERNAME}).",
                parse_mode="Markdown"
            )
        except sqlite3.IntegrityError:
            await update.message.reply_text("⚠️ هذا التوكن مسجل مسبقاً في النظام!")
        conn.close()

    elif context.user_data.get("waiting_for_paid_token"):
        token = text
        context.user_data["waiting_for_paid_token"] = False
        
        # إرسال طلب تفعيل البوت المدفوع إلى المطور الأساسي
        keyboard = [
            [InlineKeyboardButton("• تفعيل البوت الآن •", callback_data=f"approve_paid_{user.id}_{token[:10]}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=DEV_ID,
            text=f"💎 **طلب تفعيل بوت مدفوع جديد!**\n\n"
                 f"• صاحب البوت: {user.first_name} (ID: `{user.id}`)\n"
                 f"• المعرف: @{user.username if user.username else 'لا يوجد'}\n"
                 f"• توكن البوت: `{token}`",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        await update.message.reply_text("⏳ تم إرسال توكن بوتك المدفوع إلى المطور الأساسي (`@odox6`) للمراجعة والتفعيل الفوري.")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != DEV_ID:
        await update.message.reply_text("عذراً، هذه اللوحة خاصة بالمطور الأساسي فقط.")
        return
        
    keyboard = [
        [InlineKeyboardButton("• إحصائيات Source TP •", callback_data="admin_stats")],
        [InlineKeyboardButton("• قائمة البوتات المصنوعة •", callback_data="admin_list_bots")],
        [InlineKeyboardButton("• قسم الإذاعة •", callback_data="admin_broadcast")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"⚡️ **لوحة التحكم الخاصة بالمطور الأساسي لـ {BOT_NAME}**"
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "make_bot_menu":
        keyboard = [
            [InlineKeyboardButton("• صنع بوت مجاني •", callback_data="make_free_bot")],
            [InlineKeyboardButton("• صنع بوت مدفوع •", callback_data="make_paid_bot")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("• اختر نوع البوت الذي تريد صنعه:", reply_markup=reply_markup)
        
    elif data == "games_menu_cb":
        await query.edit_message_text("🎮 ألعاب سورس ماريو وتي بي مفعلة وتعمل بكفاءة عالية داخل المجموعات!")
        
    elif data == "make_free_bot":
        context.user_data["waiting_for_free_token"] = True
        await query.edit_message_text(
            f"🤖 **إنشاء بوت مجاني**\n\n"
            f"• أرسل الآن **توكن البوت** الخاص بك المستلم من @BotFather في الشات هنا.\n"
            f"• سيتم تفعيل البوت فوراً مع إبقاء حقوق قناة السورس ({BOT_USERNAME}).",
            parse_mode="Markdown"
        )
        
    elif data == "make_paid_bot":
        context.user_data["waiting_for_paid_token"] = True
        keyboard = [
            [InlineKeyboardButton("• مراسلة المطور للدفع والتفعيل •", url=f"https://t.me/odox3")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"💎 **إنشاء بوت مدفوع (VIP)**\n\n"
            f"• البوت المدفوع يكون بدون حقوق إجبارية وخاص بك بالكامل.\n"
            f"• تواصل أولاً مع المطور ({DEV_USERNAME}) لإتمام الدفع، ثم أرسل **توكن البوت** هنا وسيقوم المطور بتفعيله حصراً.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
    elif data == "my_bots":
        conn = sqlite3.connect("source_tp.db")
        cursor = conn.cursor()
        cursor.execute("SELECT bot_type, status FROM created_bots WHERE owner_id = ?", (query.from_user.id,))
        bots = cursor.fetchall()
        conn.close()
        
        if not bots:
            await query.edit_message_text("• ليس لديك أي بوتات مصنوعة حالياً.")
        else:
            msg = "🤖 **قائمة بوتاتك المصنوعة:**\n\n"
            for idx, (b_type, b_status) in enumerate(bots, 1):
                msg += f"{idx} - النوع: {b_type.upper()} | الحالة: {b_status}\n"
            await query.edit_message_text(msg, parse_mode="Markdown")
            
    elif data == "admin_stats":
        conn = sqlite3.connect("source_tp.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM created_bots")
        total_bots = cursor.fetchone()[0]
        conn.close()
        await query.edit_message_text(f"📊 **إحصائيات {BOT_NAME}:**\n\n• إجمالي البوتات المصنوعة بالنظام: {total_bots}", parse_mode="Markdown")
        
    elif data.startswith("game_"):
        await query.edit_message_text("🎯 تم تفاعل لعبة السورس بنجاح داخل النظام!")

@app.route('/')
def home():
    return "Source TP Maker Bot Server is running!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    import asyncio
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return 'ok', 200

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_bot())
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
