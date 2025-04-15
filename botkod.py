import json
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, \
    ConversationHandler, filters

# توکن ربات
BOT_TOKEN = "7231667091:AAF7ErllhYpfRjLzq8Msof9vX5cjU1x4ZXU"

# مسیر عکس خوش‌آمدگویی
IMAGE_PATH = "D:/python.py/pttttttt.png"

# فایل دیتا
DATA_FILE = "data.json"

# آی‌دی ادمین‌ها
ADMINS = [5928722311]


# بارگذاری دیتا
def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"codes": {}, "channel_name": "سریال آنلاین"}, f)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data.get("codes", {}), dict):
            data["codes"] = {}
        return data


# ذخیره دیتا
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# شروع (/start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()

    msg = f"""این ربات چه می‌کند؟\n\nربات کد دهی کانال فیلم 90\n\nکانال [{data['channel_name']}]\n\nکد خود را وارد کنید و پاداش دریافت کنید\nلطفاً کد را صحیح وارد کنید"""

    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 انتخاب کد", callback_data="choose_code")],
        [InlineKeyboardButton("💬 ارتباط با پشتیبانی", url="https://t.me/pren76")]
    ])

    try:
        with open(IMAGE_PATH, "rb") as img:
            await update.message.reply_photo(
                photo=img,
                caption=msg,
                reply_markup=inline_keyboard
            )
    except Exception as e:
        print("❌ خطا در ارسال عکس:", e)
        await update.message.reply_text("❌ ارسال عکس با مشکل مواجه شد.\n\n" + msg, reply_markup=inline_keyboard)


# مرحله‌های افزودن کد
SET_CODE = range(1)
REMOVE_CODE = range(2)


async def ask_for_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        await update.message.reply_text("لطفاً ۵ کد ۸ رقمی را با + جدا کرده ارسال کنید.",
                                        reply_markup=ReplyKeyboardRemove())
        return SET_CODE
    else:
        await update.message.reply_text("⛔ دسترسی فقط برای ادمین است.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


async def save_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    codes = [code.strip() for code in text.split("+") if len(code.strip()) == 8]

    if not codes:
        await update.message.reply_text("❗ لطفاً کدهای ۸ کاراکتری را با + از هم جدا کنید.")
        return ConversationHandler.END

    data = load_data()
    added, skipped = [], []

    for code in codes:
        if code not in data["codes"]:
            data["codes"][code] = []
            added.append(code)
        else:
            skipped.append(code)

    save_data(data)
    msg = f"✅ کدهای اضافه شده: {', '.join(added)}" if added else "⚠️ هیچ کدی اضافه نشد."
    if skipped:
        msg += f"\n🔁 کدهای تکراری: {', '.join(skipped)}"
    await update.message.reply_text(msg)
    return ConversationHandler.END


# حذف همه کدها
async def ask_for_removal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        await update.message.reply_text(
            "🔻 تایید کنید که می‌خواهید تمام کدها حذف شوند. هر متنی ارسال کنید تا ادامه یابد.")
        return REMOVE_CODE
    else:
        await update.message.reply_text("⛔ دسترسی فقط برای ادمین است.")
        return ConversationHandler.END


async def confirm_remove_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMINS:
        data = load_data()
        data["codes"] = {}
        save_data(data)
        await update.message.reply_text("🗑️ تمام کدها با موفقیت حذف شدند.")
    else:
        await update.message.reply_text("⛔ دسترسی فقط برای ادمین است.")
    return ConversationHandler.END


# نمایش کدها
async def show_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        data = load_data()
        codes_data = data.get("codes", {})

        if isinstance(codes_data, dict) and codes_data:
            codes = list(codes_data.keys())
            await update.message.reply_text("📋 کدهای فعلی:\n" + "\n".join(codes))
        else:
            await update.message.reply_text("⚠️ هیچ کدی ثبت نشده است.")
    else:
        await update.message.reply_text("⛔ دسترسی فقط برای ادمین است.")


# لغو عملیات
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_code"] = False
    await update.message.reply_text("⛔ عملیات لغو شد.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# تغییر نام کانال
async def change_channel_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ADMINS:
        text = update.message.text.replace("تغییر اسم کانال", "").strip()
        data = load_data()
        data["channel_name"] = text
        save_data(data)
        await update.message.reply_text("✅ نام کانال تغییر کرد.")
    else:
        await update.message.reply_text("⛔ دسترسی فقط برای ادمین است.")


# دکمه انتخاب کد
async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "choose_code":
        context.user_data["awaiting_code"] = True
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ لغو ارسال کد", callback_data="cancel_code")]
        ])
        await query.message.reply_text(
            "🎯 لطفاً کد ۸ رقمی خود را ارسال کنید.\n\nمیتونی چندین کد وارد کنی. برای خروج روی دکمه زیر بزن.",
            reply_markup=keyboard)

    elif query.data == "cancel_code":
        context.user_data["awaiting_code"] = False
        await query.message.reply_text("❌ ارسال کد متوقف شد.")


# بررسی کد وارد شده
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    data = load_data()

    if context.user_data.get("awaiting_code"):
        if text in data["codes"]:
            if user.id not in data["codes"][text]:
                data["codes"][text].append(user.id)
                save_data(data)
                try:
                    user_profile_photos = await context.bot.get_user_profile_photos(user.id)
                    photo_file_id = None
                    if user_profile_photos.total_count > 0:
                        photo_file_id = user_profile_photos.photos[0][0].file_id

                    for admin_id in ADMINS:
                        caption = (
                            f"✅ کاربر جدید کد صحیح وارد کرد:\n\n"
                            f"👤 نام: {user.first_name}\n"
                            f"🆔 عددی: {user.id}\n"
                            f"📛 یوزرنیم: @{user.username if user.username else 'ندارد'}\n"
                            f"🔢 کد وارد شده: {text}"
                        )
                        if photo_file_id:
                            await context.bot.send_photo(chat_id=admin_id, photo=photo_file_id, caption=caption)
                        else:
                            await context.bot.send_message(chat_id=admin_id, text=caption)
                except Exception as e:
                    print("خطا در ارسال به ادمین:", e)
                await update.message.reply_text("✅ با موفقیت کد وارد شد. شما یک امتیاز گرفتید.")
            else:
                await update.message.reply_text("⚠️ شما قبلاً از این کد استفاده کرده‌اید.")
        else:
            await update.message.reply_text("❌ کد وارد شده اشتباه است یا وجود ندارد.")
        context.user_data["awaiting_code"] = True

    elif update.effective_user.id in ADMINS:
        await update.message.reply_text("ℹ️ برای افزودن کد از دستور /setcod استفاده کنید.")


# اجرای ربات
if __name__ == "__main__":
    print("🤖 ربات در حال اجراست...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()


    async def set_commands(app):
        await app.bot.set_my_commands([
            BotCommand("start", "شروع ربات"),
            BotCommand("setcod", "افزودن کد جدید (ادمین)"),
            BotCommand("showcodes", "نمایش کدها (ادمین)"),
            BotCommand("removecode", "حذف همه کدها (ادمین)"),
            BotCommand("cancel", "لغو عملیات فعلی")
        ])


    app.post_init = set_commands

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_inline_buttons))
    app.add_handler(CommandHandler("showcodes", show_codes))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("setcod", ask_for_codes)],
        states={SET_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_codes)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("removecode", ask_for_removal)],
        states={REMOVE_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_remove_code)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    ))

    app.add_handler(MessageHandler(filters.Regex("^تغییر اسم کانال.*"), change_channel_name))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()
