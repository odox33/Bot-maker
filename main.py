import os
import asyncio
from pyrogram import Client, filters

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

API_ID = 36216701
API_HASH = "dbba65547d24e32dd37ac3dbm2885ef"
BOT_TOKEN = "8704690798:AAEshhQ2o0qFuy6UwHbVGWq-a"

app = Client(
    "SourceTPBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text(
        "👋 **أهلاً بك في سورس تي بي لصانع البوتات والخدمات**\n\n"
        "🤖 **البوت يعمل الآن 24/7 بنجاح على سحابة Render**\n\n"
        "📌 **الأوامر المتاحة:**\n"
        "• `/id` - لعرض معلوماتك أو الشخص.\n"
        "• `/ban` - لطرد أو حظر عضو بالمجموعة.\n"
        "• `/make` - لصنع بوت جديدة.\n"
        "• `/games` - الألعاب الترفيهية.\n"
        "• `/youtube` - للبحث في اليوتيوب."
    )

@app.on_message(filters.command("id"))
async def id_command(client, message):
    user = message.from_user
    await message.reply_text(
        f"🆔 **معلومات الحساب:**\n"
        f"• الاسم : {user.first_name}\n"
        f"• الأي دي : `{user.id}`\n"
        f"• اليوزر : @{user.username if user.username else 'لا يوجد'}"
    )

@app.on_message(filters.command("ban") & filters.group)
async def ban_command(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ يرجى الرد على رسالة العضو المراد حظره!")
    user_id = message.reply_to_message.from_user.id
    await message.chat.ban_member(user_id)
    await message.reply_text("✅ تم حظر العضو بنجاح!")

@app.on_message(filters.command("make"))
async def make_bot(client, message):
    await message.reply_text("🛠 **قريباً سيتم تفعيل قسم صنع النسخ والخدمات في سورس تي بي.**")

@app.on_message(filters.command("games"))
async def games_menu(client, message):
    await message.reply_text("🎮 **أهلاً بك في الألعاب الترفيهية ضمن سورس تي بي.**")

@app.on_message(filters.command("youtube"))
async def youtube_search(client, message):
    await message.reply_text("📺 **قسم البحث في اليوتيوب ضمن سورس تي بي.**")

if __name__ == "__main__":
    app.run()
