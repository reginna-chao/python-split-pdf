import fitz  # PyMuPDF
from PIL import Image, ImageEnhance
import io
import sys

def split_pdf_with_brightness(input_path, output_path, dpi=300, brightness_factor=1.15):
    doc = fitz.open(input_path)
    new_doc = fitz.open()

    a4_width_pt = 210 / 25.4 * 72  # 約 595.28 pt
    scale = dpi / 72

    for page_index in range(len(doc)):
        page = doc[page_index]
        rect = page.rect
        full_height = rect.height

        for i in range(3):
            x0 = i * a4_width_pt
            x1 = x0 + a4_width_pt
            clip = fitz.Rect(x0, 0, x1, full_height)

            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)

            # 將 pixmap 轉成 PIL Image
            image = Image.open(io.BytesIO(pix.tobytes("ppm")))
            
            # 調整亮度
            enhancer = ImageEnhance.Brightness(image)
            bright_img = enhancer.enhance(brightness_factor)

            # 轉成 pixmap
            img_byte_arr = io.BytesIO()
            bright_img.save(img_byte_arr, format="PNG")
            img_byte_arr.seek(0)
            bright_pix = fitz.Pixmap(fitz.csRGB, fitz.open("png", img_byte_arr).get_page_pixmap(0))

            new_page = new_doc.new_page(width=a4_width_pt, height=full_height)
            new_page.insert_image(new_page.rect, pixmap=bright_pix)

    new_doc.save(output_path)
    print(f"✅ 已亮化輸出：{output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python split_pdf_bright.py input.pdf output.pdf")
    else:
        split_pdf_with_brightness(sys.argv[1], sys.argv[2])
