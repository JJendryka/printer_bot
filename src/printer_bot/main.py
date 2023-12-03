"""Main module of printer_bot."""

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
from brother_ql.backends.helpers import send
from brother_ql.conversion import convert
from brother_ql.raster import BrotherQLRaster


def print_test_image() -> None:
    """Print test image."""
    qlr = BrotherQLRaster("QL-700")
    instructions = convert(qlr=qlr, images=["test_image.png"], label="12")
    send(instructions=instructions, printer_identifier="usb://0x04f9:0x2042", backend_identifier="pyusb", blocking=True)


def create_image(text: str) -> PIL.Image.Image:
    """Create image with text."""
    font = PIL.ImageFont.truetype("OpenSans-Regular.ttf", 60)
    length = int(font.getlength(text))
    img = PIL.Image.new("1", (length, 106), color=1)
    draw = PIL.ImageDraw.ImageDraw(img)
    draw.text((0, 0), text, 0, font=font)
    return img.rotate(90, expand=True)


def print_pillow_image(image: PIL.Image.Image) -> None:
    """Print PIL image on printer."""
    qlr = BrotherQLRaster("QL-700")
    instructions = convert(qlr=qlr, images=[image], label="12")
    send(instructions=instructions, printer_identifier="usb://0x04f9:0x2042", backend_identifier="pyusb", blocking=True)


if __name__ == "__main__":
    img = create_image("Testowy tekst")
    print_pillow_image(img)
