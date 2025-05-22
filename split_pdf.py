import fitz  # PyMuPDF
import sys
import os
from dotenv import load_dotenv

def mm_to_pt(mm):
    return mm / 25.4 * 72  # mm → point

def split_pdf_with_image_rendering_and_bleed(input_path, output_path, dpi=300):
    load_dotenv()
    bleed_mm = float(os.getenv("PRINT_BLEED", "0"))
    bleed_pt = mm_to_pt(bleed_mm)

    doc = fitz.open(input_path)
    new_doc = fitz.open()

    a4_width_pt = mm_to_pt(210)
    a4_height_pt = mm_to_pt(297)
    scale = dpi / 72

    for page_index in range(len(doc)):
        page = doc[page_index]
        rect = page.rect
        full_height = rect.height

        for i in range(3):
            # 原始切割區域
            x0 = i * a4_width_pt
            x1 = x0 + a4_width_pt
            y0 = 0
            y1 = full_height

            # 移除出血範圍
            clip = fitz.Rect(
                x0 + bleed_pt,
                y0 + bleed_pt,
                x1 - bleed_pt,
                y1 - bleed_pt
            )

            # 將 clip 區塊渲染成高解析度圖像
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)

            # 新頁尺寸為 clip 寬高
            width_pt = clip.width
            height_pt = clip.height

            new_page = new_doc.new_page(width=width_pt, height=height_pt)
            new_page.insert_image(new_page.rect, pixmap=pix)

    new_doc.save(output_path)
    print(f"✅ 已輸出 PDF（裁掉 {bleed_mm}mm 出血）：{output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python split_pdf_with_bleed.py input.pdf output.pdf")
    else:
        split_pdf_with_image_rendering_and_bleed(sys.argv[1], sys.argv[2])