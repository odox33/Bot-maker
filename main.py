import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

API_ID = 36216701
API_HASH = "f95bac8547d34e32dd37ec3cdbe28558"
BOT_TOKEN = "8704690798:AAEShhQ2o0qFuy6UwHbVGwQ-aAVlcA8FI_w"

app = Client(
    "SourceTPBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# القائمة الرئيسية والأزرار
@app.on_message(filters.command(["start", "الاوامر", "البداية"]))
async def start_command(client, message):
    text = (
        " Tb \n"
        "الاوامر\n\n"
        "▫️ - اليك اوامر سورس تي بي ⚡️⚡️\n\n"
        "▫️ - [ م 1 ] ↜ اوامر الحمايه\n"
        "▫️ - [ م 2 ] ↜ اوامر المشرفين\n"
        "▫️ - [ م 3 ] ↜ اوامر التفعيلات\n"
        "▫️ - [ م 4 ] ↜ اوامر المسح\n"
        "▫️ - [ م 5 ] ↜ اوامر المطورين\n"
        "▫️ - [ م 6 ] ↜ اوامر الترفيه"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("• 1 •", callback_data="sec_1"), InlineKeyboardButton("• 2 •", callback_data="sec_2")],
        [InlineKeyboardButton("• 3 •", callback_data="sec_3")],
        [InlineKeyboardButton("• 4 •", callback_data="sec_4"), InlineKeyboardButton("• 5 •", callback_data="sec_5")],
        [InlineKeyboardButton("• 6 •", callback_data="sec_6")]
    ])
    
    await message.reply_text(text, reply_markup=keyboard)

# معالجة الضغط على الأزرار الشفافة
@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    
    if data == "sec_1":
        await callback_query.message.edit_text(
            "🛡 **قائمة اوامر الحمايه (م 1):**\n\n• قفل الكصر\n• قفل الروابط\n• قفل التوجيه\n• منع التكرار",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« رجوع", callback_data="back_home")]])
        )
    elif data == "sec_2":
        await callback_query.message.edit_text(
            "👮‍♂️ **قائمة اوامر المشرفين (م 2):**\n\n• كتم / اسكات\n• حظر / طرد\n• تثبيت رسالة\n• رفع مشرف",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« رجوع", callback_data="back_home")]])
        )
    elif data == "sec_3":
        await callback_query.message.edit_text(
            "⚙️ **قائمة اوامر التفعيلات (م 3):**\n\n• تفعيل الردود\n• تفعيل الترحيب\n• تفعيل الالعاب",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« رجوع", callback_data="back_home")]])
        )
    elif data == "sec_4":
        await callback_query.message.edit_text(
            "🗑 **قائمة اوامر المسح (م 4):**\n\n• مسح المكتومين\n• مسح المحظورين\n• مسح الإداريين",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« رجوع", callback_data="back_home")]])
        )
    elif data == "sec_5":
        await callback_query.message.edit_text(
            "⚡️ **قائمة اوامر المطورين (م 5):**\n\n• اذاعة عامة\n• احصائيات البوت\n• تحديث السورس",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« رجوع", callback_data="back_home")]])
        )
    elif data == "sec_6":
        await callback_query.message.edit_text(
            "🎮 **قائمة اوامر الترفيه (م 6):**\n\n• قسم الالعاب\n• المقرعة\n• زارف / صيد",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« رجوع", callback_data="back_home")]])
        )
    elif data == "back_home":
        text = (
            " Tb \n"
            "الاوامر\n\n"
            "▫️ - اليك اوامر سورس تي بي ⚡️⚡️\n\n"
            "▫️ - [ م 1 ] ↜ اوامر الحمايه\n"
            "▫️ - [ م 2 ] ↜ اوامر المشرفين\n"
            "▫️ - [ م 3 ] ↜ اوامر التفعيلات\n"
            "▫️ - [ م 4 ] ↜ اوامر المسح\n"
            "▫️ - [ م 5 ] ↜ اوامر المطورين\n"
            "▫️ - [ م 6 ] ↜ اوامر الترفيه"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("• 1 •", callback_data="sec_1"), InlineKeyboardButton("• 2 •", callback_data="sec_2")],
            [InlineKeyboardButton("• 3 •", callback_data="sec_3")],
            [InlineKeyboardButton("• 4 •", callback_data="sec_4"), InlineKeyboardButton("• 5 •", callback_data="sec_5")],
            [InlineKeyboardButton("• 6 •", callback_data="sec_6")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)

if __name__ == "__main__":
    app.run()
