import fitz  # PyMuPDF
import sys
import os
import glob
from dotenv import load_dotenv

def mm_to_pt(mm):
    return mm / 25.4 * 72

def get_env_value(key, default_value, value_type=str):
    """安全地從環境變數取得值，自動清理註解和空白"""
    value = os.getenv(key, str(default_value)).strip()
    
    # 移除行內註解
    if '#' in value:
        value = value.split('#')[0].strip()
    
    try:
        if value_type == int:
            return int(value)
        elif value_type == float:
            return float(value)
        elif value_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        else:
            return value
    except (ValueError, AttributeError):
        print(f"⚠️  警告: {key} 設定值無效 '{value}'，使用預設值 '{default_value}'")
        return default_value

def split_pdf_with_bleed_and_order(input_path, output_path, dpi=300):
    load_dotenv()

    # 讀取設定
    bleed_mm = get_env_value("PRINT_BLEED", 0, float)
    bleed_pt = mm_to_pt(bleed_mm)
    page_order_str = get_env_value("PAGE_ORDER", "")
    
    # 壓縮設定
    compress_images = get_env_value("COMPRESS_IMAGES", True, bool)
    image_quality = get_env_value("IMAGE_QUALITY", 85, int)
    compress_pdf = get_env_value("COMPRESS_PDF", True, bool)
    output_dpi = get_env_value("OUTPUT_DPI", dpi, int)

    try:
        doc = fitz.open(input_path)
        temp_pages = []
        a4_width_pt = mm_to_pt(210)
        
        # 根據壓縮設定調整scale
        if compress_pdf and output_dpi != dpi:
            scale = output_dpi / 72
        else:
            scale = dpi / 72

        # 切割每一頁成3個A4
        for page_num in range(len(doc)):
            page = doc[page_num]
            rect = page.rect

            # 從左到右切3折，每折都裁掉出血
            for fold in range(3):
                x0 = fold * a4_width_pt + bleed_pt
                x1 = (fold + 1) * a4_width_pt - bleed_pt
                y0 = bleed_pt
                y1 = rect.height - bleed_pt

                clip = fitz.Rect(x0, y0, x1, y1)
                mat = fitz.Matrix(scale, scale)
                
                # 取得pixmap
                if compress_images:
                    # 壓縮模式：使用較低DPI和JPEG壓縮
                    pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)
                    # 轉換為JPEG格式來壓縮
                    img_data = pix.tobytes("jpeg", jpg_quality=image_quality)
                    temp_pages.append((clip.width, clip.height, img_data, "jpeg"))
                else:
                    # 原始模式：保持PNG格式
                    pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)
                    temp_pages.append((clip.width, clip.height, pix, "pixmap"))

        total_cut_pages = len(temp_pages)

        # 處理排序
        if page_order_str:
            try:
                # 使用者輸入的是1-based，轉成0-based
                page_order = [int(n) - 1 for n in page_order_str.strip().split(",")]
                
                # 檢查順序是否有效
                if len(page_order) != total_cut_pages:
                    print(f"❌ 錯誤: PAGE_ORDER 有 {len(page_order)} 個數字，但切出了 {total_cut_pages} 頁")
                    doc.close()
                    return False
                    
                if any(i < 0 or i >= total_cut_pages for i in page_order):
                    print(f"❌ 錯誤: PAGE_ORDER 中有無效的頁面編號 (應該是1-{total_cut_pages})")
                    doc.close()
                    return False
                    
                order = page_order
            except ValueError:
                print("❌ PAGE_ORDER 格式錯誤，應該像這樣: 1,2,3,4,5,6")
                doc.close()
                return False
        else:
            order = list(range(total_cut_pages))

        # 組成新PDF
        new_doc = fitz.open()
        
        for new_pos, old_idx in enumerate(order):
            width, height, img_data, img_type = temp_pages[old_idx]
            
            # 建立新頁面，使用裁切後的尺寸
            page = new_doc.new_page(width=width, height=height)
            
            if img_type == "jpeg":
                # 插入JPEG圖片
                page.insert_image(page.rect, stream=img_data)
            else:
                # 插入pixmap
                page.insert_image(page.rect, pixmap=img_data)

        # 儲存PDF（帶壓縮選項）
        if compress_pdf:
            # 先儲存到臨時檔案，然後進行進階壓縮
            temp_output = output_path + ".temp"
            new_doc.save(temp_output, 
                        garbage=4,      # 清理未使用物件
                        deflate=True,   # 啟用deflate壓縮
                        clean=True)     # 清理和優化
            new_doc.close()
            
            # 重新開啟進行進階壓縮
            compressed_doc = fitz.open(temp_output)
            
            # 進階壓縮：重新處理每一頁
            final_doc = fitz.open()
            for page_num in range(len(compressed_doc)):
                page = compressed_doc[page_num]
                
                # 如果啟用圖片壓縮，重新渲染頁面
                if compress_images:
                    # 用較低DPI重新渲染
                    compress_scale = output_dpi / 72
                    mat = fitz.Matrix(compress_scale, compress_scale)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    
                    # 轉JPEG壓縮
                    img_data = pix.tobytes("jpeg", jpg_quality=image_quality)
                    
                    # 建立新頁面並插入壓縮圖片
                    new_page = final_doc.new_page(width=page.rect.width, height=page.rect.height)
                    new_page.insert_image(new_page.rect, stream=img_data)
                else:
                    # 直接複製頁面
                    final_doc.insert_pdf(compressed_doc, from_page=page_num, to_page=page_num)
            
            # 最終儲存
            final_doc.save(output_path,
                          garbage=4,        # 清理未使用物件
                          deflate=True,     # 啟用deflate壓縮  
                          clean=True,       # 清理和優化
                          linear=True)      # 線性化PDF (網頁友善)
            
            final_doc.close()
            compressed_doc.close()
            
            # 刪除臨時檔案
            try:
                os.remove(temp_output)
            except:
                pass
        else:
            new_doc.save(output_path)
            new_doc.close()
        
        doc.close()
        return True
        
    except Exception as e:
        print(f"❌ 處理 {input_path} 時發生錯誤: {str(e)}")
        return False

def process_batch():
    """批次處理input資料夾中的所有PDF"""
    load_dotenv()
    
    # 讀取設定
    bleed_mm = get_env_value("PRINT_BLEED", 0, float)
    page_order_str = get_env_value("PAGE_ORDER", "")
    compress_images = get_env_value("COMPRESS_IMAGES", True, bool)
    image_quality = get_env_value("IMAGE_QUALITY", 85, int)
    compress_pdf = get_env_value("COMPRESS_PDF", True, bool)
    output_dpi = get_env_value("OUTPUT_DPI", 300, int)
    
    print("🚀 批次PDF處理工具")
    print("=" * 50)
    print(f"🔧 設定:")
    print(f"  出血: {bleed_mm}mm")
    print(f"  頁面順序: {page_order_str if page_order_str else '預設順序'}")
    print(f"  圖片壓縮: {'開啟' if compress_images else '關閉'}")
    if compress_images:
        print(f"  圖片品質: {image_quality}%")
    print(f"  PDF壓縮: {'開啟' if compress_pdf else '關閉'}")
    if output_dpi != 300:
        print(f"  輸出DPI: {output_dpi}")
    print("=" * 50)
    
    # 檢查input資料夾
    input_dir = "input"
    output_dir = "output"
    
    if not os.path.exists(input_dir):
        print(f"❌ 找不到 {input_dir} 資料夾")
        print(f"請建立 {input_dir} 資料夾並放入要處理的PDF檔案")
        return
    
    # 建立output資料夾
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ 已建立 {output_dir} 資料夾")
    
    # 尋找所有PDF檔案
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    pdf_files.extend(glob.glob(os.path.join(input_dir, "*.PDF")))  # 支援大寫副檔名
    
    if not pdf_files:
        print(f"❌ 在 {input_dir} 資料夾中找不到PDF檔案")
        return
    
    print(f"📁 找到 {len(pdf_files)} 個PDF檔案:")
    for i, pdf_file in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_file)
        print(f"  {i}. {filename}")
    
    print("\n🔄 開始處理...")
    
    success_count = 0
    error_count = 0
    
    for i, input_pdf in enumerate(pdf_files, 1):
        filename = os.path.basename(input_pdf)
        name_without_ext = os.path.splitext(filename)[0]
        output_pdf = os.path.join(output_dir, f"{name_without_ext}_processed.pdf")
        
        print(f"\n📄 [{i}/{len(pdf_files)}] 處理: {filename}")
        
        # 檢查輸出檔案是否已存在
        if os.path.exists(output_pdf):
            print(f"⚠️  輸出檔案已存在: {os.path.basename(output_pdf)}")
            response = input("是否覆蓋? (y/n): ").lower().strip()
            if response != 'y':
                print("⏭️  跳過此檔案")
                continue
        
        # 處理PDF
        if split_pdf_with_bleed_and_order(input_pdf, output_pdf):
            success_count += 1
            
            # 顯示檔案大小比較
            try:
                original_size = os.path.getsize(input_pdf)
                output_size = os.path.getsize(output_pdf)
                compression_ratio = (1 - output_size / original_size) * 100
                
                print(f"✅ 完成: {os.path.basename(output_pdf)}")
                print(f"📊 檔案大小: {original_size / 1024 / 1024:.1f}MB → {output_size / 1024 / 1024:.1f}MB", end="")
                if compression_ratio > 0:
                    print(f" (壓縮 {compression_ratio:.1f}%)")
                else:
                    print(f" (增加 {abs(compression_ratio):.1f}%)")
            except:
                print(f"✅ 完成: {os.path.basename(output_pdf)}")
        else:
            error_count += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 批次處理完成!")
    print(f"✅ 成功: {success_count} 個檔案")
    if error_count > 0:
        print(f"❌ 失敗: {error_count} 個檔案")
    print(f"📁 輸出位置: {output_dir}/")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 沒有參數，執行批次處理
        process_batch()
    elif len(sys.argv) == 3:
        # 有兩個參數，執行單檔處理
        if split_pdf_with_bleed_and_order(sys.argv[1], sys.argv[2]):
            print("✅ 處理完成!")
        else:
            print("❌ 處理失敗!")
    else:
        print("用法:")
        print("1. 批次處理: python split_pdf.py")
        print("   (處理 input/*.pdf → output/*_processed.pdf)")
        print("2. 單檔處理: python split_pdf.py input.pdf output.pdf")
        print("\n設定檔 .env 範例:")
        print("PRINT_BLEED=3")
        print("PAGE_ORDER=3,6,1,2,4,5")
        print("COMPRESS_IMAGES=true")
        print("IMAGE_QUALITY=85")
        print("COMPRESS_PDF=true")
        print("OUTPUT_DPI=150")