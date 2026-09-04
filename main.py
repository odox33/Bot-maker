import os
from pyrogram import Client, filters

# بيانات البوت الخاصة بك
API_ID = 36216701
API_HASH = "dbba65547d24e32dd37ac3cdbe2885ef"
BOT_TOKEN = "8704690798:AAEShhQ2o0qFuy6UwHbVGwQ-aAVlcA8FI_w"

app = Client(
    "BotMaker",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 **أهلاً بك في سورس صانع بوتات الحماية والخدمات!**\n\n"
        "🤖 البوت يعمل الآن 24/7 بنجاح على سحابة Render.\n"
        "📌 الأوامر المتاحة:\n"
        "• /id - لعرض معلوماتك أو الشخص.\n"
        "• /ban - لطرد أو حظر عضواً بالمجموعة.\n"
        "• /make - لصنع نسخة بوت جديدة.\n"
        "• /games - قسم الألعاب والتسلية.\n"
        "• /youtube - للتحميل والبحث عبر يوتيوب."
    )

@app.on_message(filters.command("id"))
async def id_command(client, message):
    user = message.from_user
    await message.reply_text(
        f"🆔 **معلومات الحساب:**\n"
        f"• الاسم: {user.first_name}\n"
        f"• الأيدي: `{user.id}`\n"
        f"• اليوزر: @{user.username if user.username else 'لا يوجد'}"
    )

@app.on_message(filters.command("ban") & filters.group)
async def ban_command(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ بالرد على رسالة الشخص المراد طرده!")
    user_id = message.reply_to_message.from_user.id
    await message.chat.ban_member(user_id)
    await message.reply_text("✅ تم طرد العضو بنجاح!")

@app.on_message(filters.command("make"))
async def make_bot(client, message):
    await message.reply_text("🛠 **قسم صنع النسخ:**\nارسل توكن البوت الجديد الذي ترغب بإنشائه لربطه بالنظام.")

@app.on_message(filters.command("games"))
async def games_menu(client, message):
    await message.reply_text("🎮 **قائمة الألعاب الترفيهية:**\n1. لعبة الرفيق\n2. حظوظ\n*(قريباً يتم تفعيل باقي الألعاب)*")

@app.on_message(filters.command("youtube"))
async def youtube_search(client, message):
    await message.reply_text("📺 **قسم اليوتيوب:**\nارسل اسم الفيديو أو الرابط للبحث والتحميل.")

printimport asyncio



async def main():
    print("Bot is starting...")
    await app.start()
    print("Bot is online!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())



