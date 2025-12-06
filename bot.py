import json
import datetime
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)


# === JSON FAYLLARNI O'QISH/Yozish ===
def load_admins():
    try:
        with open("admins.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_admins(admins):
    with open("admins.json", "w") as f:
        json.dump(admins, f)


def load_workers():
    try:
        with open("workers.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_workers(workers):
    with open("workers.json", "w") as f:
        json.dump(workers, f)


# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("📍 LIVE lokatsiya yuborish", request_location=True)]]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Assalomu alaykum!\n\n"
        "Ma'lumotlarni birma-bir yuboring:\n"
        "1) Ism Familiya\n"
        "2) Ishga kelganingizni tasdiqlovchi rasm\n"
        "3) LIVE Location (jonli joylashuv)",
        reply_markup=reply
    )

    workers = load_workers()
    if update.message.chat_id not in workers:
        workers.append(update.message.chat_id)
        save_workers(workers)


# === Hodim ismi ===
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ism"] = update.message.text
    await update.message.reply_text("Endi ishga kelgan rasmingizni yuboring 📸")


# === Rasm ===
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["photo"] = update.message.photo[-1].file_id
    await update.message.reply_text("Endi LIVE lokatsiyani yuboring 📍")


# === LIVE LOCATION qabul qilish va ADMINga yuborish ===
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    admins = load_admins()

    ism = context.user_data.get("ism")
    photo_id = context.user_data.get("photo")

    ish_vaqti = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for admin in admins:
        # BARCHA MA’LUMOTLAR BITTA XABARDA
        await context.bot.send_message(
            chat_id=admin,
            text=f"👤 Hodim: {ism}\n"
                 f"⏰ Ishga kelgan vaqt: {ish_vaqti}\n"
                 f"📍 LIVE Lokatsiya quyida ⤵️"
        )

        # Jonli lokatsiya
        await context.bot.send_location(
            chat_id=admin,
            latitude=loc.latitude,
            longitude=loc.longitude,
            live_period=3600  # 1 soat jonli
        )

        # Rasmni yuborish
        await context.bot.send_photo(
            chat_id=admin,
            photo=photo_id
        )

    await update.message.reply_text("Ma'lumot boshliqqa yuborildi!")


# === ADMIN qo'shish ===
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = load_admins()

    if update.message.chat_id not in admins:
        return await update.message.reply_text("Siz admin emassiz.")

    if len(context.args) == 0:
        return await update.message.reply_text("ID kiriting: /addadmin 123456")

    new_admin = int(context.args[0])
    if new_admin not in admins:
        admins.append(new_admin)
        save_admins(admins)
        await update.message.reply_text("Yangi admin qo'shildi.")
    else:
        await update.message.reply_text("Bu foydalanuvchi allaqachon admin.")


# === ADMINLAR ro'yxati ===
async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = load_admins()
    text = "Adminlar:\n" + "\n".join(map(str, admins))
    await update.message.reply_text(text)


# === Hodimlar ro'yxati ===
async def list_workers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    workers = load_workers()
    text = "Hodimlar ro'yxati:\n" + "\n".join(map(str, workers))
    await update.message.reply_text(text)


# === Botni ishga tushirish ===
def main():
    app = ApplicationBuilder().token("8497779102:AAF3RE1MuqSubdnAeLWDbIRNR1ZKIaMm9sA").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("admins", list_admins))
    app.add_handler(CommandHandler("workers", list_workers))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
