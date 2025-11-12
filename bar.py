import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

SPACING = 20          # space between stacked barcodes
PADDING_X = 20        # left/right padding around each barcode block
PADDING_TOP = 20      # space above each barcode image
LABEL_GAP = 8         # gap between barcode and its label
LABEL_SIZE = 20       # font size for the label text
BG = "white"
FG = "black"

def make_barcode_image(data: str) -> Image.Image:
    """Return a PIL image: barcode with its text label underneath as one block."""
    # Render the barcode directly to a PIL image (no temp files)
    code = barcode.get("code128", data, writer=ImageWriter())
    # Tweak module size/text as desired
    writer_opts = {
        "module_height": 20.0,      # bar height
        "module_width": 0.4,        # bar thickness
        "quiet_zone": 6.0,          # sides padding for scanners
        "font_size": 0,             # we draw our own label, so turn off built-in text
        "background": BG,
        "foreground": FG,
        "text_distance": 0,
        "write_text": False,
    }
    barcode_img = code.render(writer_options=writer_opts)  # PIL.Image

    # Prepare label image
    try:
        # Use a default font (monospace not guaranteed in container)
        font = ImageFont.load_default(size=LABEL_SIZE)  # type: ignore
    except TypeError:
        font = ImageFont.load_default()

    # Measure label
    draw_tmp = ImageDraw.Draw(barcode_img)
    bbox = draw_tmp.textbbox((0, 0), data, font=font)
    label_w = bbox[2] - bbox[0]
    label_h = bbox[3] - bbox[1]

    # Compose a block with padding + label
    block_w = max(barcode_img.width + 2 * PADDING_X, label_w + 2 * PADDING_X)
    block_h = PADDING_TOP + barcode_img.height + LABEL_GAP + label_h + PADDING_TOP

    block = Image.new("RGB", (block_w, block_h), BG)
    # center barcode
    x_bar = (block_w - barcode_img.width) // 2
    y_bar = PADDING_TOP
    block.paste(barcode_img, (x_bar, y_bar))

    # center label
    draw = ImageDraw.Draw(block)
    x_lbl = (block_w - label_w) // 2
    y_lbl = y_bar + barcode_img.height + LABEL_GAP
    draw.text((x_lbl, y_lbl), data, font=font, fill=FG)

    return block

def combine_blocks(blocks: list[Image.Image], output_file="barcodes_sheet.png"):
    """Stack multiple barcode+label blocks vertically into one sheet."""
    if not blocks:
        print("⚠️ No barcodes to save.")
        return

    max_w = max(img.width for img in blocks)
    total_h = sum(img.height for img in blocks) + SPACING * (len(blocks) - 1)

    sheet = Image.new("RGB", (max_w, total_h), BG)
    y = 0
    for i, img in enumerate(blocks):
        x = (max_w - img.width) // 2
        sheet.paste(img, (x, y))
        y += img.height + (SPACING if i < len(blocks) - 1 else 0)
        img.close()

    sheet.save(output_file)
    print(f"✅ Saved all barcodes to {output_file}")

if __name__ == "__main__":
    print("📦 Multi-Barcode Sheet (type 'done' to finish)\n")
    blocks: list[Image.Image] = []

    while True:
        data = input("Enter text for barcode (or 'done' to stop): ").strip()
        if not data or data.lower() == "done":
            break
        try:
            blocks.append(make_barcode_image(data))
        except Exception as e:
            print(f" Failed to create barcode for '{data}': {e}")

    if blocks:
        combine_blocks(blocks, output_file="barcodes_sheet.png")
    else:
        print("⚠️ Nothing entered. No file created.")
