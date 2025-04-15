import json
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, \
    ConversationHandler, filters

BOT_TOKEN = "7231667091:AAF7ErllhYpfRjLzq8Msof9vX5cjU1x4ZXU"
IMAGE_PATH = "D:/python.py/pttttttt.png"
DATA_FILE = "data.json"
ADMINS = [5928722311, 5921101573]

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"codes": {}, "channel_name": "سریال آنلاین", "admins": ADMINS}, f)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "admins" not in data:
            data["admins"] = ADMINS
        return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
            await update.message.reply_photo(photo=img, caption=msg, reply_markup=inline_keyboard)
    except:
        await update.message.reply_text("❌ ارسال عکس با مشکل مواجه شد.\n\n" + msg, reply_markup=inline_keyboard)

SET_CODE = range(1)
REMOVE_CODE = range(2)

async def ask_for_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in load_data()["admins"]:
        await update.message.reply_text("۵ کد ۸ رقمی را با + جدا کنید:", reply_markup=ReplyKeyboardRemove())
        return SET_CODE
    else:
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
    msg = f"✅ اضافه شده: {', '.join(added)}" if added else "⚠️ هیچ کدی اضافه نشد."
    if skipped:
        msg += f"\n🔁 تکراری: {', '.join(skipped)}"
    await update.message.reply_text(msg)
    return ConversationHandler.END

async def ask_for_removal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in load_data()["admins"]:
        await update.message.reply_text("🔻 تایید کنید. هر متنی ارسال کنید.")
        return REMOVE_CODE
    else:
        return ConversationHandler.END

async def confirm_remove_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in load_data()["admins"]:
        data = load_data()
        data["codes"] = {}
        save_data(data)
        await update.message.reply_text("🗑️ همه کدها حذف شدند.")
    return ConversationHandler.END

async def show_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in load_data()["admins"]:
        codes = list(load_data()["codes"].keys())
        await update.message.reply_text("📋 کدها:\n" + "\n".join(codes) if codes else "⚠️ هیچ کدی نیست.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["awaiting_code"] = False
    await update.message.reply_text("⛔ لغو شد.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def change_channel_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in load_data()["admins"]:
        text = update.message.text.replace("تغییر اسم کانال", "").strip()
        data = load_data()
        data["channel_name"] = text
        save_data(data)
        await update.message.reply_text("✅ اسم کانال تغییر کرد.")

async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "choose_code":
        context.user_data["awaiting_code"] = True
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ لغو ارسال کد", callback_data="cancel_code")]])
        await query.message.reply_text("🎯 لطفاً کد خود را بفرست:", reply_markup=keyboard)
    elif query.data == "cancel_code":
        context.user_data["awaiting_code"] = False
        await query.message.reply_text("❌ ارسال کد متوقف شد.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    data = load_data()
    if context.user_data.get("awaiting_code"):
        if text in data["codes"]:
            if user.id not in data["codes"][text]:
                data["codes"][text].append(user.id)
                save_data(data)
                for admin in data["admins"]:
                    msg = f"✅ کاربر جدید:\n👤 {user.first_name}\n🆔 {user.id}\n📛 @{user.username or 'ندارد'}\n🔢 کد: {text}"
                    try:
                        photos = await context.bot.get_user_profile_photos(user.id)
                        if photos.total_count > 0:
                            await context.bot.send_photo(admin, photo=photos.photos[0][0].file_id, caption=msg)
                        else:
                            await context.bot.send_message(admin, msg)
                    except:
                        pass
                await update.message.reply_text("✅ کد صحیح بود. امتیاز گرفتید.")
            else:
                await update.message.reply_text("⚠️ قبلاً از این کد استفاده کردید.")
        else:
            await update.message.reply_text("❌ کد اشتباه است.")
        context.user_data["awaiting_code"] = True
    elif user.id in data["admins"]:
        await update.message.reply_text("ℹ️ برای افزودن کد از /setcod استفاده کن.")

# دستور جدید: افزودن ادمین
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in load_data()["admins"]:
        return
    if not context.args:
        await update.message.reply_text("🆔 آیدی عددی کاربر را وارد کن: /addadmin 123456789")
        return
    new_admin_id = int(context.args[0])
    data = load_data()
    if new_admin_id in data["admins"]:
        await update.message.reply_text("⛔ این کاربر قبلاً ادمین بوده.")
    else:
        data["admins"].append(new_admin_id)
        save_data(data)
        await update.message.reply_text(f"✅ کاربر {new_admin_id} به لیست ادمین‌ها اضافه شد.")

# دستور جدید: تغییر نام ربات
async def set_bot_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in load_data()["admins"]:
        return
    new_name = " ".join(context.args)
    if not new_name:
        await update.message.reply_text("📝 نام جدید را وارد کن: /setname اسم_جدید")
        return
    try:
        await context.bot.set_my_name(name=new_name)
        await update.message.reply_text("✅ نام ربات تغییر یافت.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

# دستور جدید: تغییر عکس پروفایل
async def set_bot_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in load_data()["admins"]:
        return
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        await context.bot.set_my_profile_photo(photo=file)
        await update.message.reply_text("✅ عکس ربات با موفقیت تغییر یافت.")
    else:
        await update.message.reply_text("📷 لطفاً یک عکس ارسال کنید.")

if __name__ == "__main__":
    print("🤖 ربات در حال اجراست...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    async def set_commands(app):
        await app.bot.set_my_commands([
            BotCommand("start", "شروع"),
            BotCommand("setcod", "افزودن کد"),
            BotCommand("showcodes", "نمایش کدها"),
            BotCommand("removecode", "حذف همه کدها"),
            BotCommand("addadmin", "افزودن ادمین"),
            BotCommand("setname", "تغییر نام ربات"),
            BotCommand("cancel", "لغو"),
        ])

    app.post_init = set_commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_inline_buttons))
    app.add_handler(CommandHandler("showcodes", show_codes))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("setname", set_bot_name))
    app.add_handler(MessageHandler(filters.PHOTO, set_bot_photo))

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
