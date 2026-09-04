import os
import sqlite3
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_NAME = "Source TP"
BOT_USERNAME = "@odox6"
DEV_ID = 8297163405
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ==================== قاعدة البيانات الضخمة (SQLITE3) ====================
db_conn = sqlite3.connect("source_tp_ultimate_pro.db", check_same_thread=False)
cursor = db_conn.cursor()

# جداول متعددة مثل السورسات الكبرى (المجموعات، الحماية، الصد والردود، الألعاب)
cursor.execute("CREATE TABLE IF NOT EXISTS active_groups (chat_id INTEGER PRIMARY KEY, status TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS group_settings (chat_id INTEGER PRIMARY KEY, lock_link TEXT, lock_flood TEXT, lock_bots TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS custom_replies (chat_id INTEGER, keyword TEXT, reply_text TEXT)")
db_conn.commit()

# ==================== بدء البوت والواجهة الترحيبية ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        keyboard = [
            [InlineKeyboardButton("➕ أضف البوت لمجموعتك", url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [InlineKeyboardButton("قناة السورس", url=f"https://t.me/{BOT_USERNAME.replace('@','')}")]
        ]
        await update.message.reply_text(
            f"مرحباً بك في بوت **{BOT_NAME}** 🤖🔥\n\n"
            "• السورس الأقوى لإدارة وحماية المجموعات (يحتوي على كافة أوامر الإدارة، الحماية، التسلية، والمطور).\n"
            "• أضفني إلى مجموعتك وارفعني مشرفاً، ثم اكتب **تفعيل** للبدء!",
            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )

# ==================== معالج الأوامر الشامل (أكثر من نظام وقسم) ====================
async def ultimate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    text = update.message.text.strip()
    chat = update.effective_chat
    user = update.effective_user
    
    # ---------------- 1. قسم التفعيل والتعطيل ----------------
    if text == "تفعيل":
        if chat.type == "private":
            await update.message.reply_text("• هذا الأمر خاص بالمجموعات فقط!")
            return
        cursor.execute("INSERT OR REPLACE INTO active_groups (chat_id, status) VALUES (?, ?)", (chat.id, "active"))
        cursor.execute("INSERT OR IGNORE INTO group_settings (chat_id, lock_link, lock_flood, lock_bots) VALUES (?, ?, ?, ?)", (chat.id, "مفعل", "مفعل", "مفعل"))
        db_conn.commit()
        await update.message.reply_text("✅ **تم تفعيل البوت بنجاح!**\n\n• تم فتح كافة أقسام الحماية، الأيدي، الإدارة، والتسلية لهذا القروب.", parse_mode="Markdown")
        return

    elif text == "تعطيل":
        if chat.type == "private":
            return
        cursor.execute("DELETE FROM active_groups WHERE chat_id = ?", (chat.id,))
        db_conn.commit()
        await update.message.reply_text("❌ **تم تعطيل البوت في هذه المجموعة.**")
        return

    # التحقق هل القروب مفعل
    if chat.type != "private":
        cursor.execute("SELECT status FROM active_groups WHERE chat_id = ?", (chat.id,))
        res = cursor.fetchone()
        if not res or res[0] != "active":
            return

    # ---------------- 2. قسم الأيدي المتطور (مثل السورسات الكبرى) ----------------
    if text in ["ايدي", "الاي دي", "ايديي", "/id", "ID"]:
        user_status = "عضو 👤"
        if user.id == DEV_ID:
            user_status = "مطور السورس 💻"
        else:
            try:
                member = await chat.get_member(user.id)
                if member.status == "creator":
                    user_status = "منشئ المجموعة 👑"
                elif member.status == "administrator":
                    user_status = "مشرف المجموعة ⭐"
            except:
                pass

        id_msg = (
            f"• ⦗ أيديك ⦘ : ` {user.id} `\n"
            f"• ⦗ معرفك ⦘ : @{user.username if user.username else 'لا يوجد'}\n"
            f"• ⦗ اسمك ⦘ : {user.first_name}\n"
            f"• ⦗ رتبتك ⦘ : {user_status}\n"
            f"• ⦗ ايدي القروب ⦘ : ` {chat.id} `\n"
            f"• ⦗ اسم القروب ⦘ : {chat.title}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"• ⦗ السورس ⦘ : {BOT_NAME} ({BOT_USERNAME})"
        )

        try:
            photos = await context.bot.get_user_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                await update.message.reply_photo(photo=photos.photos[0][0].file_id, caption=id_msg, parse_mode="Markdown")
            else:
                await update.message.reply_text(id_msg, parse_mode="Markdown")
        except:
            await update.message.reply_text(id_msg, parse_mode="Markdown")

    # ---------------- 3. قسم الحماية والإدارة والتحكم بالأعضاء ----------------
    elif text in ["طرد", "انقلع"] and update.message.reply_to_message:
        try:
            target = update.message.reply_to_message.from_user
            await context.bot.ban_chat_member(chat.id, target.id)
            await update.message.reply_text(f"🔨 تم طرد العضو [{target.first_name}](tg://user?id={target.id}) بنجاح.", parse_mode="Markdown")
        except:
            await update.message.reply_text("⚠️ لا أملك صلاحية الطرد أو أن الشخص مشرف!")

    elif text == "كتم" and update.message.reply_to_message:
        try:
            target = update.message.reply_to_message.from_user
            await context.bot.restrict_chat_member(chat.id, target.id, permissions={"can_send_messages": False})
            await update.message.reply_text(f"🔇 تم كتم العضو {target.first_name}.")
        except:
            await update.message.reply_text("⚠️ لا أملك صلاحية الكتم!")

    elif text == "الغاء كتم" and update.message.reply_to_message:
        try:
            target = update.message.reply_to_message.from_user
            await context.bot.restrict_chat_member(chat.id, target.id, permissions={
                "can_send_messages": True, "can_send_media_messages": True, "can_send_other_messages": True, "can_add_web_page_previews": True
            })
            await update.message.reply_text(f"🔊 تم إلغاء كتم العضو {target.first_name}.")
        except:
            await update.message.reply_text("⚠️ خطأ في الصلاحيات!")

    elif text == "تثبيت" and update.message.reply_to_message:
        try:
            await context.bot.pin_chat_message(chat.id, update.message.reply_to_message.message_id)
            await update.message.reply_text("📌 تم تثبيت الرسالة بنجاح.")
        except:
            await update.message.reply_text("⚠️ لا أملك صلاحية التثبيت!")

    # ---------------- 4. قسم رفع وترقية المشرفين ----------------
    elif text == "رفع مشرف" and update.message.reply_to_message:
        try:
            target = update.message.reply_to_message.from_user
            await context.bot.promote_chat_member(
                chat.id, target.id,
                can_manage_chat=True, can_delete_messages=True, can_invite_users=True, can_restrict_members=True
            )
            await update.message.reply_text(f"⭐ تم ترقية العضو {target.first_name} إلى مشرف.")
        except:
            await update.message.reply_text("⚠️ لا أملك صلاحية رفع المشرفين!")

    elif text == "تنزيل مشرف" and update.message.reply_to_message:
        try:
            target = update.message.reply_to_message.from_user
            await context.bot.promote_chat_member(
                chat.id, target.id,
                can_manage_chat=False, can_delete_messages=False, can_invite_users=False, can_restrict_members=False
            )
            await update.message.reply_text(f"🔻 تم تنزيل العضو {target.first_name} من الإشراف.")
        except:
            await update.message.reply_text("⚠️ لا أملك صلاحية إزالة المشرفين!")

    # ---------------- 5. قسم التسلية والألعاب (مثل سورسات ماريو) ----------------
    elif text in ["حزورة", "لغز"]:
        puzzles = [
            "• ما هو الشيء الذي يبكي بلا عينين ويصيخ بلا أذنين؟ (البصل)",
            "• شيء يتكلم جميع لغات العالم فما هو؟ (صدى الصوت)",
            "• من هو الـذي يرى عدوه وصديقه بنفس الوضوح؟ (الأعور)",
            "• ما هو البيت الذي ليس فيه أبواب ولا نوافذ؟ (بيت الشعر)"
        ]
        await update.message.reply_text(random.choice(puzzles))

    elif text == "نسبة الحب":
        love_rate = random.randint(30, 100)
        await update.message.reply_text(f"❤️ نسبة الحب بينك وبين القروب هي : `{love_rate}%` 😍", parse_mode="Markdown")

    elif text == "سؤال":
        questions = [
            "• لو خيروك بين المال أو العائلة؟",
            "• ما هي أمنيتك الوحيدة الي تبي تحققها اليوم؟",
            "• شنو أكلتك المفضلة؟",
            "• أكتر صفة تكرهها بالناس شنو هي؟"
        ]
        await update.message.reply_text(random.choice(questions))

    # ---------------- 6. قسم الأوامر العامة والمطور ----------------
    elif text in ["المطور", "مطور السورس"]:
        await update.message.reply_text(
            f"• معلومات مطور السورس الأساسي:\n"
            f"• ايدي المطور : `{DEV_ID}`\n"
            f"• قناة السورس : {BOT_USERNAME}\n"
            f"• نظام السورس : Ultimate Pro (متكامل).",
            parse_mode="Markdown"
        )

    elif text.startswith("اذاعة") and user.id == DEV_ID:
        broadcast_text = text.replace("اذاعة", "").strip()
        if broadcast_text:
            cursor.execute("SELECT chat_id FROM active_groups")
            all_groups = cursor.fetchall()
            count = 0
            for g in all_groups:
                try:
                    await context.bot.send_message(g[0], f"📢 **إعلان رسمي من المطور:**\n\n{broadcast_text}", parse_mode="Markdown")
                    count += 1
                except:
                    pass
            await update.message.reply_text(f"✅ تم إرسال الإذاعة بنجاح إلى `{count}` مجموعة.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ultimate_handler))
    print("Source TP Ultimate Pro is running successfully...")
    application.run_polling()

if __name__ == "__main__":
    main()
