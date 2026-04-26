import logging
from io import BytesIO
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(level=logging.INFO)

# Store user images
user_images = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send multiple images.\nType /done to get a single PDF."
    )

# Handle images
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id

        photo = update.message.photo[-1]
        file = await photo.get_file()

        img_bytes = BytesIO()
        await file.download_to_memory(out=img_bytes)
        img_bytes.seek(0)

        img = Image.open(img_bytes)

        if img.mode != "RGB":
            img = img.convert("RGB")

        user_images.setdefault(user_id, []).append(img)

        await update.message.reply_text("✅ Image added")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# /done command
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id

        if user_id not in user_images or not user_images[user_id]:
            await update.message.reply_text("⚠️ No images found")
            return

        images = user_images[user_id]
        pdf_bytes = BytesIO()

        images[0].save(
            pdf_bytes,
            format="PDF",
            save_all=True,
            append_images=images[1:]
        )

        pdf_bytes.seek(0)

        await update.message.reply_document(
            document=pdf_bytes,
            filename="output.pdf"
        )

        user_images[user_id] = []

        await update.message.reply_text("📄 PDF sent!")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# Main function
def main():
    import os
TOKEN = os.getenv("simple_pdf_creater_bot")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
