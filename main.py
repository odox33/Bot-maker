import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

API_ID = 36216701
API_HASH = "f95bac8547d34e32dd37ec3cdbe28558"
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "SourceTPBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

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

@app.on_message(filters.command(["start", "الاوامر", "البداية"]))
async def start_command(client, message):
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
    await message.reply_text(start_text, reply_markup=start_keyboard)

@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    
    if data == "sec_1":
        text = (
            "Tb\n"
            "الاوامر\n\n"
            "- : اوامر ( القفل والفتح ) ⚡️⚡️\n"
            "- : تستطيع القفل ⚡️⚡️\n\n"
            "• التاك • القنوات\n"
            "• الصور • الروابط\n"
            "• الفشار • التكرار\n"
            "• الفيديو • الدخول\n"
            "• الاضافه • الاغاني\n"
            "• الصوت • الملفات\n"
            "• التفليش • الدردشه\n"
            "• الجهات • السيلفي\n"
            "• التثبيت • الشارحه\n"
            "• الكلايش • البوتات\n"
            "• التوجيه • التعديل\n"
            "• المعرفات • الكيبورد\n"
            "• الفارسيه • الانجليزيه\n"
            "• الملصقات • الاشعارات\n"
            "• الماركداون • المتحركه"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("• 2 •", callback_data="sec_2")],
            [InlineKeyboardButton("• 3 •", callback_data="sec_3"), InlineKeyboardButton("• 4 •", callback_data="sec_4")],
            [InlineKeyboardButton("• 5 •", callback_data="sec_5"), InlineKeyboardButton("• 6 •", callback_data="sec_6")],
            [InlineKeyboardButton("• القائمه الرئيسيه •", callback_data="back_home")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)

    elif data == "sec_2":
        text = (
            "Tb\n"
            "الاوامر\n\n"
            "- : اوامر مشرفين المجموعه ⚡️⚡️\n"
            "- : الاوامر تعمل بامر ( الكتابة )\n\n"
            "• القوائم • الميديا\n"
            "• نزلني • انذار\n"
            "• تصفير الترند\n"
            "• ضبط الحمايه\n"
            "• تثبيت • الاعدادات\n"
            "• الردود المميزه\n"
            "• الردود المتعدده\n"
            "• الاوامر المضافه\n"
            "• ضع التكرار + العدد\n"
            "• التفعيلات • صلاحياتي\n"
            "• اضيف رد • اضيف امر\n"
            "• تاك للكل • ضع رابط\n"
            "• وضع تاك • تغيير المالك\n"
            "• ضع ترحيب • ضع توحيد\n"
            "• انشاء رابط • قائمه المنع\n"
            "• الغاء التثبيت • تعيين الايدي\n"
            "• تغيير الايدي • منع • الغاء منع\n"
            "• اضيف رد متعدد\n"
            "• الغاء تثبيت الكل • كشف البوتات\n"
            "• ضع عدد المسح + العدد\n"
            "• اضيف نقاط + العدد بالرد\n"
            "• اضيف رسائل + العدد بالرد"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("• 1 •", callback_data="sec_1")],
            [InlineKeyboardButton("• 3 •", callback_data="sec_3"), InlineKeyboardButton("• 4 •", callback_data="sec_4")],
            [InlineKeyboardButton("• 5 •", callback_data="sec_5"), InlineKeyboardButton("• 6 •", callback_data="sec_6")],
            [InlineKeyboardButton("• القائمه الرئيسيه •", callback_data="back_home")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)

    elif data == "sec_3":
        text = (
            "Tb\n"
            "الاوامر\n\n"
            "- : اوامر التفعيل و التعطيل ⚡️⚡️\n"
            "- : الاوامر تعمل بامر ( الكتابة )\n\n"
            "• نداء • نبذه\n"
            "• نزلني • التاك\n"
            "• الرفع • غنيلي\n"
            "• الرابط • التنبيه\n"
            "• الاهداء • الحظر\n"
            "• الايدي • صورتي\n"
            "• اسمي • التفاعل\n"
            "• التوحيد • الالعاب\n"
            "• اطردني • الهمسه\n"
            "• التحذير • الترحيب\n"
            "• المضاد • ثنائي اليوم\n"
            "• ردود البوت • ايدي العضو\n"
            "• الوضع الليلي • الايدي بالصوره\n"
            "• المسح التلقائي • الحظر المحدد\n"
            "• المسح التلقائي بالوقت"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("• 1 •", callback_data="sec_1"), InlineKeyboardButton("• 2 •", callback_data="sec_2")],
            [InlineKeyboardButton("• 4 •", callback_data="sec_4")],
            [InlineKeyboardButton("• 5 •", callback_data="sec_5"), InlineKeyboardButton("• 6 •", callback_data="sec_6")],
            [InlineKeyboardButton("• القائمه الرئيسيه •", callback_data="back_home")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)

    elif data == "sec_4":
        text = (
            "Tb\n"
            "الاوامر\n\n"
            "- : اوامر الرفع والحظر ⚡️⚡️\n"
            "- : الاوامر تعمل بامر ( الكتابة )\n\n"
            "• طرد • تحكم\n"
            "• تقييد بالوقت\n"
            "• اضيف تاك • تنزيل الكل\n"
            "• رفع المالك • رفع القيود\n"
            "• رفع الادمنيه • كشف القيود\n"
            "• كتم • الغاء كتم\n"
            "• حظر • الغاء حظر\n"
            "• تقييد • الغاء تقييد\n"
            "• رفع • تنزيل {منشئ}\n"
            "• رفع • تنزيل {مدير}\n"
            "• رفع • تنزيل {ادمن}\n"
            "• رفع • تنزيل {مميز}\n"
            "• رفع • تنزيل {مشرف}\n"
            "• رفع • تنزيل {منشئ اساسي}\n"
            "• تغيير • مسح كليشه المالك\n"
            "• تقييد {رقم} يوم • ساعة • دقيقة\n\n"
            "- : ارسل الامر لاظهار القائمة\n\n"
            "• المدراء • المالك\n"
            "• الادمنيه • المميزين\n"
            "• المقيدين • المكتومين\n"
            "• المحظورين • المشرفين\n"
            "• المنشئين • المنشئين الاساسيين"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("• 1 •", callback_data="sec_1"), InlineKeyboardButton("• 2 •", callback_data="sec_2")],
            [InlineKeyboardButton("• 3 •", callback_data="sec_3")],
            [InlineKeyboardButton("• 6 •", callback_data="sec_6")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)

    elif data == "sec_5":
        text = (
            "Tb\n"
            "الاوامر\n\n"
            "- : اوامر مسح المشرفين ⚡️⚡️\n"
            "- : الاوامر تعمل بامر ( الكتابة )\n\n"
            "• رد • تاك\n"
            "• امر • الرابط\n"
            "• رد عام • الايدي\n"
            "• المدراء • التحذير\n"
            "• الترحيب • رد مميز\n"
            "• المنشئين • المالكين\n"
            "• الادمنيه • المميزين\n"
            "• المقيدين • رد متعدد\n"
            "• المكتومين • قائمه المنع\n"
            "• المطرودين • المحظورين\n"
            "• الثانويين • المطورين\n"
            "• كليشه المالك • قائمه التاكات\n"
            "• المميزين عام • كليشه المطور\n"
            "• مسح + العدد • الردود المميزه\n"
            "• الردود المتعدده • قائمه المنع العام\n"
            "• المنشئين الاساسيين"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("• 1 •", callback_data="sec_1"), InlineKeyboardButton("• 2 •", callback_data="sec_2")],
            [InlineKeyboardButton("• 3 •", callback_data="sec_3")],
            [InlineKeyboardButton("• 5 •", callback_data="sec_5"), InlineKeyboardButton("• 6 •", callback_data="sec_6")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)

    elif data == "sec_6":
        text = (
            "Tb\n"
            "الاوامر\n\n"
            "- : اوامر ترفيه الاعضاء ⚡️⚡️\n"
            "- : الاوامر تعمل بامر ( الكتابة )\n\n"
            "• نداء • جمالي\n"
            "• زوجني • الالعاب\n"
            "• ثنائي اليوم • الحب\n"
            "• الكره • الرجوله\n"
            "• الانوثه • الجمال\n"
            "• الالعاب الاحترافيه\n"
            "• غنيلي • اني\n"
            "• صوره • اغنيه\n"
            "• متحركه • ميمز\n"
            "• ريمكس • افتار\n"
            "• ثيم • راب\n"
            "• شعر • قصيده\n"
            "• اقتباس • ستوري\n"
            "• قران • جداريه\n"
            "• هينه • هينها\n"
            "• طلقني • طلقيني\n"
            "• زوجي • زوجتي\n"
            "• الازواج • المتزوجين\n"
            "- رفع • تنزيل ↜ مطي\n"
            "- رفع • تنزيل ↜ ملك\n"
            "- رفع • تنزيل ↜ ملكه\n"
            "- رفع • تنزيل ↜ جلب\n"
            "- رفع • تنزيل ↜ زاحف\n"
            "- رفع • تنزيل ↜ زاحفه\n"
            "- رفع • تنزيل ↜ كيك\n"
            "- رفع • تنزيل ↜ كيمر\n"
            "- رفع • تنزيل ↜ مرتي\n"
            "- رفع • تنزيل ↜ من كلبي"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("• 1 •", callback_data="sec_1"), InlineKeyboardButton("• 2 •", callback_data="sec_2")],
            [InlineKeyboardButton("• 3 •", callback_data="sec_3"), InlineKeyboardButton("• 4 •", callback_data="sec_4")],
            [InlineKeyboardButton("• القائمه الرئيسيه •", callback_data="back_home")]
        ])
        await callback_query.message.edit_text(text, reply_markup=keyboard)

    elif data == "back_home":
        await callback_query.message.edit_text(MAIN_TEXT, reply_markup=MAIN_KEYBOARD)

async def main():
    print("Starting bot manually...")
    await app.start()
    print("Bot started successfully!")
    await asyncio.Future()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_loop_exit = False
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
