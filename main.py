# ==============================================================================
# سورس اندريس (النسخة الكبرى المطورة والموسعة - الجزء الأول والأساسي)
# يحتوي على نظام قواعد البيانات المتقدم، إدارة المجموعات، ونظام الحماية الشامل
# ==============================================================================

import os
import sys
import time
import random
import sqlite3
import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ------------------------------------------------------------------------------
# إعدادات التسجيل واللوغ (Logging Configuration)
# ------------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DEV_USERNAME = os.getenv("DEV_USERNAME", "YOUR_USERNAME")

# ------------------------------------------------------------------------------
# هيكلة وتصميم قاعدة البيانات الشاملة (SQLite Massive Core)
# ------------------------------------------------------------------------------
def init_massive_database():
    database_name = "bot_ultimate_source_1200plus.db"
    connection = sqlite3.connect(database_name, check_same_thread=False)
    cursor = connection.cursor()
    
    # جدول المستخدمين الشامل والنقاط
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users_registry (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance INTEGER DEFAULT 500,
            bank_balance INTEGER DEFAULT 1500,
            experience_points INTEGER DEFAULT 0,
            user_level INTEGER DEFAULT 1,
            warnings_count INTEGER DEFAULT 0,
            reputation INTEGER DEFAULT 0,
            spouse_id INTEGER DEFAULT 0,
            is_banned_globally INTEGER DEFAULT 0,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # جدول إعدادات المجموعات والحماية المتقدمة
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups_protection_settings (
            chat_id INTEGER PRIMARY KEY,
            anti_links INTEGER DEFAULT 1,
            anti_spam_flood INTEGER DEFAULT 1,
            anti_arabic_spam INTEGER DEFAULT 0,
            anti_bots_join INTEGER DEFAULT 1,
            anti_forwards INTEGER DEFAULT 0,
            anti_media_spam INTEGER DEFAULT 0,
            lock_group_chat INTEGER DEFAULT 0,
            welcome_message TEXT DEFAULT 'أهلاً بك عزيزي العضو في قصر المملكة العريق!'
        )
    """)
    
    # جدول الردود المخصصة التفاعلية
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_bot_replies (
            trigger_keyword TEXT PRIMARY KEY,
            response_text TEXT
        )
    """)
    
    # جدول المشرفين المخصصين والرتب الإدارية
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_bot_admins (
            user_id INTEGER PRIMARY KEY,
            admin_rank_title TEXT
        )
    """)
    
    # جدول قائمة الحظر العام للمخربين
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_blacklisted_users (
            user_id INTEGER PRIMARY KEY,
            ban_reason TEXT
        )
    """)
    
    # جدول المتجر والرتب المشتراة
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_shop_inventory (
            user_id INTEGER,
            item_name TEXT,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

# تنفيذ إنشاء قاعدة البيانات فوراً
init_massive_database()

def verify_developer_privileges(user_id: int, username: str) -> bool:
    if username and username.lower() == DEV_USERNAME.lower():
        return True
    conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM custom_bot_admins WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

# ------------------------------------------------------------------------------
# نظام الألعاب والتسلية المتقدم والمتكامل (Games Sub-System)
# ------------------------------------------------------------------------------
async def display_games_hub_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 حجر النرد السريع", callback_data="game_dice_roll"),
         InlineKeyboardButton("🎯 رمي السهم بدقة", callback_data="game_dart_throw")],
        [InlineKeyboardButton("⚽ ركلات الجزاء", callback_data="game_football_shoot"),
         InlineKeyboardButton("🎰 ماكينة الحظ (سلوتس)", callback_data="game_slots_spin")],
        [InlineKeyboardButton("💰 حظك اليوم المالي", callback_data="game_daily_luck"),
         InlineKeyboardButton("🥷 سرقة البنك الكبرى", callback_data="game_bank_robbery")],
        [InlineKeyboardButton("🪙 طش و صك (عملة)", callback_data="game_coin_flip"),
         InlineKeyboardButton("📊 ملفك المالي الشامل", callback_data="game_user_profile")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu_return")]
    ]
    text = "🎮 **قاعة ألعاب سورس اندريس الكبرى والمتقدمة**\nاختر لعبتك المفضلة لربح النقاط والأموال ومضاعفة رصيدك:"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def games_engine_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    callback_data = query.data

    conn = sqlite3.connect("bot_ultimate_source_1200plus.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance, bank_balance, experience_points, user_level FROM users_registry WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users_registry (user_id, username, full_name) VALUES (?, ?, ?)",
                       (user_id, query.from_user.username, query.from_user.first_name))
        conn.commit()
        balance, bank_balance, xp, level = 500, 1500, 0, 1
    else:
        balance, bank_balance, xp, level = row

    if callback_data == "game_dice_roll":
        if balance < 30:
            await query.edit_message_text("❌ رصيدك الكاش لا يكفي! تحتاج إلى 30 نقطة على الأقل.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))
            conn.close()
            return
        dice_result = random.randint(1, 6)
        earned_prize = dice_result * 20
        new_balance = balance - 30 + earned_prize
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        conn.commit()
        await query.edit_message_text(f"🎲 رميت النرد وظهر الرقم: **{dice_result}**\n🎉 ربحت: `{earned_prize}` نقطة!\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_daily_luck":
        luck_modifier = random.choice([-200, 50, 150, 300, 600, 1200, -250])
        new_balance = balance + luck_modifier
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        conn.commit()
        if luck_modifier > 0:
            await query.edit_message_text(f"🍀 حظك ممتاز اليوم! ربحت **{luck_modifier}** نقطة.\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))
        else:
            await query.edit_message_text(f"💀 حظك سيء للأسف! خسرت **{abs(luck_modifier)}** نقطة.\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_bank_robbery":
        if balance < 60:
            await query.edit_message_text("❌ تحتاج إلى 60 نقطة كاش لتدبير تفاصيل عملية السرقة.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))
            conn.close()
            return
        is_successful = random.choice([True, False, True])
        if is_successful:
            stolen_loot = random.randint(250, 950)
            new_balance = balance + stolen_loot
            cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_balance, user_id))
            conn.commit()
            await query.edit_message_text(f"🥷 تمت عملية السطو على البنك بنجاح تام!\n💎 غنيمتك: `{stolen_loot}` نقطة.\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))
        else:
            new_balance = balance - 60
            cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_balance, user_id))
            conn.commit()
            await query.edit_message_text(f"🚨 فشلت خطة السرقة وقبض عليك الحراس!\n💸 غرامة مالية: 60 نقطة.\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_coin_flip":
        coin_side = random.choice(["صورة الملك", "كتابة التاريخ"])
        prize_val = 120
        new_balance = balance + prize_val
        cursor.execute("UPDATE users_registry SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        conn.commit()
        await query.edit_message_text(f"🪙 استقرت العملة المعدنية على وجه: **{coin_side}**\n🎉 ربحت `{prize_val}` نقطة في رصيدك!\n💰 رصيدك الحالي: `{new_balance}`", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_user_profile":
        profile_string = (
            f"👤 **ملفك الشخصي والمالي الشامل:**\n\n"
            f"🆔 الآيدي الشخصي: `{user_id}`\n"
            f"📛 الاسم المسجل: {query.from_user.first_name}\n"
            f"💰 الكاش المتاح: `{balance}` نقطة\n"
            f"🏦 رصيد البنك: `{bank_balance}` نقطة\n"
            f"⭐ نقاط الخبرة XP: `{xp}`\n"
            f"🎖️ مستواك الحالي: `{level}`"
        )
        await query.edit_message_text(profile_string, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="game_hub_back")]]))

    elif callback_data == "game_hub_back":
        await display_games_hub_menu(update, context)
        conn.close()
        return

    conn.close()

# ------------------------------------------------------------------------------
# نظام المتجر والشراء المتقدم (Store Sub-System)
# ------------------------------------------------------------------------------
async def display_store_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛒 شراء رتبة VIP الملكية", callback_data="store_buy_vip"),
         InlineKeyboardButton("💍 شراء خاتم الزواج الفاخر", callback_data="store_buy_ring")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu_return")]
    ]
    text = "🏪 **متجر سورس اندريس الرسمي والمتكامل:**\nاستخدم نقاطك وأموالك المكتسبة لشراء أقوى الصلاحيات والرتب المميزة!"
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ------------------------------------------------------------------------------
# أوامر الإدارة الأساسية وحماية المجموعات (Admin & Security Controls)
# ------------------------------------------------------------------------------
async def admin_mute_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ يرجى الرد على رسالة العضو المراد كتمه وتجفيف رسائله.")
        return
    target_user = update.message.reply_to_message.from_user
    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_user.id,
            permissions={"can_send_messages": False}
        )
        await update.message.reply_text(f"🔇 تم كتم العضو [{target_user.first_name}](tg://user?id={target_user.id}) بنجاح تام.", parse_mode="Markdown")
    except Exception as error_msg:
        await update.message.reply_text(f"❌ عذراً، حدث خطأ أثناء تنفيذ الكتم: {error_msg}")

async def admin_ban_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ يرجى الرد على رسالة العضو المراد حظره نهائياً.")
        return
    target_user = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=target_user.id)
        await update.message.reply_text(f"🔨 تم حظر العضو [{target_user.first_name}](tg://user?id={target_user.id}) من المجموعة.", parse_mode="Markdown")
    except Exception as error_msg:
        await update.message.reply_text(f"❌ عذراً، لم أتمكن من حظر العضو: {error_msg}")

# نهاية الجزء الأول - أرسل لي هذه القطعة فوراً واطلب الجزء الثاني لأكمل لك السورس فوق 1200 سطر بدقة كاملة!
