import os
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8704690798:AAEShhQ2oOqFuy6UwHbVGwQ-aAVlcA8FI_w"
DEV_USERNAME = "odox3"  # معرف المطور الأساسي
CHANNEL_USERNAME = "@odox6"  # قناة السورس

# --- قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('forced_sub', 'active')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('paid_bots_active', 'active')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('free_bots_active', 'active')")
    cursor.execute("CREATE TABLE IF NOT EXISTS roles (user_id INTEGER PRIMARY KEY, role TEXT)")
    # جدول المجموعات المفعلة
    cursor.execute("CREATE TABLE IF NOT EXISTS active_groups (chat_id INTEGER PRIMARY KEY, chat_title TEXT)")
    conn.commit()
    conn.close()

def save_user(user_id, username, full_name):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)", (user_id, username, full_name))
    conn.commit()
    conn.close()

def get_setting(key):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "active"

def set_setting(key, value):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE settings SET value = ? WHERE key = ?", (value, key))
    conn.commit()
    conn.close()

def get_user_role(user_id, username):
    if username and username.lower() == DEV_USERNAME.lower():
        return "owner"
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM roles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "user"

def set_user_role(user_id, role):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO roles (user_id, role) VALUES (?, ?)", (user_id, role))
    conn.commit()
    conn.close()

def activate_group(chat_id, chat_title):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO active_groups (chat_id, chat_title) VALUES (?, ?)", (chat_id, chat_title))
    conn.commit()
    conn.close()

async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["member", "creator", "administrator"]:
            return True
    except TelegramError:
        pass
    return False

# --- الواجهة الرئيسية (تظهر حصراً للمطور الأساسي في الخاص) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    save_user(user.id, user.username, user.full_name)
    role = get_user_role(user.id, user.username)
    
    # إذا كان في مجموعة، لا نرسل لوحة الأزرار الكبيرة بل نرد رسالة ترحيبية بسيطة
    if chat.type in ["group", "supergroup"]:
        await update.message.reply_text("أهلاً بك! البوت يعمل في هذه المجموعة. اكتب **تفعيل** لتفعيل البوت رسمياً.")
        return

    # إذا كان في الخاص (الدردشة الشخصية): الواجهة الكاملة تظهر للمطور حصراً
    if role == "owner":
        keyboard = [
            [InlineKeyboardButton("⚙️ إعدادات البوت والتحكم الأساسي", callback_data="admin_settings")],
            [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
            [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
            [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
            [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_text = f"أهلاً بك يا مطورنا الأساسي في لوحة تحكم المنصة الرئيسية:"
    else:
        # للمستخدم العادي في الخاص
        keyboard = [
            [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
            [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
            [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
            [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_text = f"أهلاً بك يا {user.first_name} في منصة صناعة وإدارة البوتات."

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(text=welcome_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=welcome_text, reply_markup=reply_markup)

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"🆔 الآيدي الخاص بك هو:\n`{user.id}`", parse_mode="Markdown")

# --- معالجة الأزرار ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    role = get_user_role(user.id, user.username)
    await query.answer()
    
    if query.data == "free_bot_maker":
        free_status = get_setting("free_bots_active")
        if free_status != "active":
            await query.answer("قسم صانع البوتات المجاني متوقف حالياً من قبل الإدارة.", show_alert=True)
            return

        forced_status = get_setting("forced_sub")
        if forced_status == "active":
            is_subscribed = await check_subscription(user.id, context.bot)
            if not is_subscribed:
                keyboard = [
                    [InlineKeyboardButton("📢 اشترك في قناة السورس", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
                    [InlineKeyboardButton("✅ لقد اشتريت / تحققت", callback_data="free_bot_maker")],
                    [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
                ]
                await query.edit_message_text(
                    text=f"⚠️ **عذراً، يجب عليك الاشتراك في قناة السورس أولاً لاستخدام صانع البوتات المجاني.**\n\nالقناة: {CHANNEL_USERNAME}",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                return

        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(text="🛠 **قسم صانع البوتات المجاني:**\n\nأرسل توكن بوتك الجديد للبدء بصنعه.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "paid_bot_maker":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(text="💎 **قسم صانع البوتات المدفوع:**\n\nبوتات احترافية بدون رعاية وبدون اشتراك إجباري!\nللاشتراك تواصل مع المطور.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "dev_contact":
        keyboard = [
            [InlineKeyboardButton("💬 مراسلة المطور", url=f"https://t.me/{DEV_USERNAME}")],
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
        ]
        await query.edit_message_text(text=f"👨‍💻 **معلومات المطور:**\nالمطور: @{DEV_USERNAME}\nالقناة: {CHANNEL_USERNAME}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "get_my_id":
        keyboard = [[InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]]
        await query.edit_message_text(text=f"🆔 الآيدي الخاص بك هو:\n`{user.id}`", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        
    elif query.data == "admin_settings":
        if role == "owner":
            f_sub = "🟢 مفعل" if get_setting("forced_sub") == "active" else "🔴 معطل"
            p_bots = "🟢 مفعل" if get_setting("paid_bots_active") == "active" else "🔴 معطل"
            keyboard = [
                [InlineKeyboardButton(f"الاشتراك الإجباري: {f_sub}", callback_data="toggle_forced")],
                [InlineKeyboardButton(f"البوتات المدفوعة: {p_bots}", callback_data="toggle_paid")],
                [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
            ]
            await query.edit_message_text(text="⚙️ **لوحة إعدادات البوت والتحكم:**", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            await query.answer("هذا القسم للمطور الأساسي فقط!", show_alert=True)

    elif query.data in ["toggle_forced", "toggle_paid"]:
        if role == "owner":
            if query.data == "toggle_forced":
                curr = get_setting("forced_sub")
                set_setting("forced_sub", "disabled" if curr == "active" else "active")
            else:
                curr = get_setting("paid_bots_active")
                set_setting("paid_bots_active", "disabled" if curr == "active" else "active")
            
            f_sub = "🟢 مفعل" if get_setting("forced_sub") == "active" else "🔴 معطل"
            p_bots = "🟢 مفعل" if get_setting("paid_bots_active") == "active" else "🔴 معطل"
            keyboard = [
                [InlineKeyboardButton(f"الاشتراك الإجباري: {f_sub}", callback_data="toggle_forced")],
                [InlineKeyboardButton(f"البوتات المدفوعة: {p_bots}", callback_data="toggle_paid")],
                [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_start")]
            ]
            await query.edit_message_text(text="⚙️ **تم تحديث الإعدادات بنجاح:**", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "back_to_start":
        if role == "owner":
            keyboard = [
                [InlineKeyboardButton("⚙️ إعدادات البوت والتحكم الأساسي", callback_data="admin_settings")],
                [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
                [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
                [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
                [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("🤖 صانع البوتات المجاني", callback_data="free_bot_maker")],
                [InlineKeyboardButton("💎 صانع البوتات المدفوع", callback_data="paid_bot_maker")],
                [InlineKeyboardButton("👨‍💻 حساب المطور", callback_data="dev_contact")],
                [InlineKeyboardButton("🆔 معرفة الآيدي (ID)", callback_data="get_my_id")]
            ]
        await query.edit_message_text(text="القائمة الرئيسية:", reply_markup=InlineKeyboardMarkup(keyboard))

# --- أوامر المجموعات (تفعيل، طرد، كتم، رفع مميز/أدمن/مطور، الآيدي) ---
async def group_commands_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return
    
    chat = message.chat
    text = message.text.strip()
    user = message.from_user
    role = get_user_role(user.id, user.username)

    # 1. أمر تفعيل الكروب
    if text == "تفعيل":
        if chat.type in ["group", "supergroup"]:
            activate_group(chat.id, chat.title)
            await message.reply_text("✅ تم تفعيل البوت في هذه المجموعة بنجاح!")
            return

    # الأوامر الخاصة بالمجموعات فقط
    if chat.type not in ["group", "supergroup"]:
        return

    reply = message.reply_to_message
    target_user = reply.from_user if reply else None

    # أمر الآيدي داخل المجموعة
    if text == "الايدي" or text == "/id":
        if target_user:
            await message.reply_text(f"🆔 آيدي المستخدم {target_user.first_name} هو:\n`{target_user.id}`", parse_mode="Markdown")
        else:
            await message.reply_text(f"🆔 الآيدي الخاص بك هو:\n`{user.id}`", parse_mode="Markdown")
        return

    # أوامر الرفع والتنزيل
    if text.startswith("رفع مطور أساسي") and role == "owner":
        if target_user:
            set_user_role(target_user.id, "dev")
            await message.reply_text(f"👤 تم رفعه (مطور أساسي بنجاح): {target_user.first_name}")
    elif text.startswith("رفع أدمن") and role in ["owner", "dev"]:
        if target_user:
            set_user_role(target_user.id, "admin")
            await message.reply_text(f"👤 تم رفعه (أدمن بنجاح): {target_user.first_name}")
    elif text.startswith("رفع مميز") and role in ["owner", "dev", "admin"]:
        if target_user:
            set_user_role(target_user.id, "vip")
            await message.reply_text(f"⭐ تم رفعه (عضو مميز بنجاح): {target_user.first_name}")
            
    # أوامر الطرد والكتم
    elif text.startswith("طرد") and role in ["owner", "dev", "admin"]:
        if target_user:
            try:
                await chat.ban_member(target_user.id)
                await message.reply_text(f"🚫 تم طرد المستخدم: {target_user.first_name}")
            except Exception:
                await message.reply_text("عذراً، تأكد من صلاحيات البوت الإدارية في المجموعة.")
                
    elif text.startswith("كتم") and role in ["owner", "dev", "admin"]:
        if target_user:
            try:
                await context.bot.restrict_chat_member(chat.id, target_user.id, permissions={"can_send_messages": False})
                await message.reply_text(f"🔇 تم كتم المستخدم: {target_user.first_name}")
            except Exception:
                await message.reply_text("عذراً، تأكد من صلاحيات البوت الإدارية في المجموعة.")

def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_commands_handler))

    PORT = int(os.environ.get("PORT", "10000"))
    RENDER_URL = "https://bot-maker-1-709e.onrender.com"

    logger.info("Starting bot via Webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
