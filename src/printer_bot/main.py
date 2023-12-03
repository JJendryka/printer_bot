"""Main module of printer_bot."""

import json
from pathlib import Path
from typing import Any

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
from brother_ql.backends.helpers import send
from brother_ql.conversion import convert
from brother_ql.raster import BrotherQLRaster
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters


def create_image(text: str) -> PIL.Image.Image:
    """Create image with text."""
    font = PIL.ImageFont.truetype("OpenSans-Bold.ttf", 80)
    length = int(font.getlength(text))
    img = PIL.Image.new("1", (length, 106), color=1)
    draw = PIL.ImageDraw.ImageDraw(img)
    draw.text((0, 0), text, 0, font=font)
    return img.rotate(90, expand=True)


def print_pillow_image(image: PIL.Image.Image, printer: str) -> None:
    """Print PIL image on printer."""
    qlr = BrotherQLRaster("QL-700")
    instructions = convert(qlr=qlr, images=[image], label="12")
    send(instructions=instructions, printer_identifier=printer, backend_identifier="pyusb", blocking=True)


def print_text(text: str, printer: str) -> None:
    """Print text."""
    img = create_image(text)
    print_pillow_image(img, printer)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle new user."""
    if update.effective_chat is not None and update.effective_user is not None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"I'm a printer bot, "
            f"if you want to use me add your ID ({update.effective_user.id}) to authorized list.",
        )


async def print_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle message from user. Print if authorized."""
    if (
        update.effective_chat is not None
        and update.message is not None
        and update.message.text is not None
        and update.effective_user is not None
    ):
        if update.effective_user.id in context.bot_data["secrets"]["authorized"]:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Printing...")
            print_text(update.message.text, context.bot_data["secrets"]["printer"])
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="You are not on the list of authorized user"
            )


async def post_init(app: Application) -> None:
    """On post_init load secrets to bot_data."""
    app.bot_data["secrets"] = load_secrets()


def load_secrets() -> dict[str, Any]:
    """Load secrets json from file."""
    with Path("secrets.json").open() as f:
        return json.load(f)


def main() -> None:
    """Start the bot."""
    app = ApplicationBuilder().token(load_secrets()["token"]).post_init(post_init).build()
    start_handler = CommandHandler("start", start)
    print_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), print_command)
    app.add_handler(start_handler)
    app.add_handler(print_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
