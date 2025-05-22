import fitz  # PyMuPDF
import sys

def split_pdf_with_image_rendering(input_path, output_path, dpi=300):
    doc = fitz.open(input_path)
    new_doc = fitz.open()

    a4_width_pt = 210 / 25.4 * 72  # 595.28 pt
    scale = dpi / 72  # 渲染解析度轉換

    for page_index in range(len(doc)):
        page = doc[page_index]
        rect = page.rect
        full_height = rect.height

        for i in range(3):
            x0 = i * a4_width_pt
            x1 = x0 + a4_width_pt
            clip = fitz.Rect(x0, 0, x1, full_height)

            # 將 clip 區塊渲染成高解析度圖片
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)

            # 計算對應的實際尺寸
            width_pt = x1 - x0
            height_pt = full_height

            new_page = new_doc.new_page(width=width_pt, height=height_pt)
            new_page.insert_image(new_page.rect, pixmap=pix)

    new_doc.save(output_path)
    print(f"✅ 已輸出為圖像 PDF，保證可列印：{output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python split_pdf_image_render.py input.pdf output.pdf")
    else:
        split_pdf_with_image_rendering(sys.argv[1], sys.argv[2])
