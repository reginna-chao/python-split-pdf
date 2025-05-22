import fitz  # PyMuPDF
import sys
import os
from dotenv import load_dotenv

def mm_to_pt(mm):
    return mm / 25.4 * 72

def split_pdf_with_bleed_and_order(input_path, output_path, dpi=300):
    load_dotenv()

    # 讀取設定
    bleed_mm = float(os.getenv("PRINT_BLEED", "0"))
    bleed_pt = mm_to_pt(bleed_mm)
    page_order_str = os.getenv("PAGE_ORDER", "")
    
    print(f"🔧 出血設定: {bleed_mm}mm ({bleed_pt:.1f}pt)")
    print(f"📋 頁面順序: {page_order_str}")

    doc = fitz.open(input_path)
    temp_pages = []
    a4_width_pt = mm_to_pt(210)
    scale = dpi / 72

    print(f"\n📄 原始PDF: {len(doc)} 頁")

    # 切割每一頁成3個A4
    for page_num in range(len(doc)):
        page = doc[page_num]
        rect = page.rect
        
        print(f"\n📄 處理第 {page_num + 1} 頁 (尺寸: {rect.width:.0f} x {rect.height:.0f} pt)")

        # 從左到右切3折，每折都裁掉出血
        for fold in range(3):
            x0 = fold * a4_width_pt + bleed_pt
            x1 = (fold + 1) * a4_width_pt - bleed_pt
            y0 = bleed_pt
            y1 = rect.height - bleed_pt

            clip = fitz.Rect(x0, y0, x1, y1)
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)

            temp_pages.append((clip.width, clip.height, pix))
            cut_page_num = len(temp_pages)
            
            print(f"  第{fold+1}折 → 切割頁面 {cut_page_num} (裁切出血: {bleed_mm}mm)")

    total_cut_pages = len(temp_pages)
    print(f"\n✂️  總共切出 {total_cut_pages} 張A4")

    # 顯示切割結果的編號
    print(f"\n📋 切割頁面編號對照:")
    cut_idx = 1
    for page_num in range(len(doc)):
        fold_numbers = []
        for fold in range(3):
            fold_numbers.append(str(cut_idx))
            cut_idx += 1
        print(f"  原始第{page_num+1}頁 → 切割頁面: {', '.join(fold_numbers)}")

    # 處理排序
    if page_order_str:
        try:
            # 使用者輸入的是1-based，轉成0-based
            page_order = [int(n) - 1 for n in page_order_str.strip().split(",")]
            
            print(f"\n🔄 重新排序:")
            print(f"  原順序: {list(range(1, total_cut_pages + 1))}")
            print(f"  新順序: {[i + 1 for i in page_order]}")
            
            # 檢查順序是否有效
            if len(page_order) != total_cut_pages:
                print(f"❌ 錯誤: PAGE_ORDER 有 {len(page_order)} 個數字，但切出了 {total_cut_pages} 頁")
                return
                
            if any(i < 0 or i >= total_cut_pages for i in page_order):
                print(f"❌ 錯誤: PAGE_ORDER 中有無效的頁面編號 (應該是1-{total_cut_pages})")
                return
            
            order = page_order
        except ValueError:
            print("❌ PAGE_ORDER 格式錯誤，應該像這樣: 1,2,3,4,5,6")
            return
    else:
        order = list(range(total_cut_pages))
        print(f"\n📄 使用預設順序: {[i + 1 for i in order]}")

    # 組成新PDF
    new_doc = fitz.open()
    
    print(f"\n📄 組裝新PDF:")
    for new_pos, old_idx in enumerate(order):
        width, height, pix = temp_pages[old_idx]
        
        # 建立新頁面，使用裁切後的尺寸
        page = new_doc.new_page(width=width, height=height)
        page.insert_image(page.rect, pixmap=pix)
        
        print(f"  第{new_pos+1}頁 ← 原切割頁面{old_idx+1}")

    new_doc.save(output_path)
    new_doc.close()
    doc.close()

    print(f"\n✅ 完成! 輸出到: {output_path}")
    print(f"📊 結果: {len(order)} 張A4頁面")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python split_pdf.py input.pdf output.pdf")
        print("\n設定檔 .env 範例:")
        print("PRINT_BLEED=3")
        print("PAGE_ORDER=3,6,1,2,4,5")
    else:
        split_pdf_with_bleed_and_order(sys.argv[1], sys.argv[2])