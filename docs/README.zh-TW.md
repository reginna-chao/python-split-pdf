# 📄 用 Python 切分 PDF

一個可將寬幅 PDF 切割為三折 A4 尺寸的工具，支援：
- 出血裁切
- 自訂頁面順序
- 圖片與 PDF 結構壓縮，減少輸出檔案大小

## 🌐 各語系說明

- [English](README.md)
- [繁體中文](docs/README.zh-TW.md)

---

## 🧩 功能介紹

- ✂️ 將每頁寬幅 PDF 切割成三張 A4
- 🩸 支援裁切出血區域
- 🔢 可自訂輸出頁面順序（例如摺頁印刷需求）
- 🗜️ 支援 JPEG 圖片壓縮與 PDF 優化壓縮
- 📐 可調整輸出解析度（DPI）進一步減少檔案大小

---

## 📦 安裝需求

請先安裝以下套件：

```bash
pip install pymupdf python-dotenv
```

## 🚀 使用方式

1. 建立 `.env` 設定檔
`.env` 檔案範例如下：

```
# 出血設定（單位：mm）
PRINT_BLEED=2

# 頁面輸出順序（以逗號分隔，從1開始）
PAGE_ORDER=3,4,1,5,6,2

# 圖片壓縮開關
COMPRESS_IMAGES=true

# JPEG 壓縮品質（0~100）
IMAGE_QUALITY=85

# PDF 結構壓縮開關
COMPRESS_PDF=true

# 輸出DPI（例如: 150 可降低輸出解析度以壓縮檔案）
OUTPUT_DPI=150
```

2. 執行指令

```bash
python split_pdf.py input.pdf output.pdf
```

### ⚙️ 環境變數設定說明
| 變數名稱              | 說明                           | 範例值              |
| ----------------- | ---------------------------- | ---------------- |
| `PRINT_BLEED`     | 出血設定（裁切掉的邊緣，單位：mm）           | `2`              |
| `PAGE_ORDER`      | 輸出頁面順序（以逗號分隔，從1開始）           | `3,4,1,5,6,2`    |
| `COMPRESS_IMAGES` | 是否啟用圖片壓縮                     | `true` / `false` |
| `IMAGE_QUALITY`   | JPEG 壓縮品質（0\~100）            | `85`             |
| `COMPRESS_PDF`    | 是否啟用 PDF 結構壓縮                | `true` / `false` |
| `OUTPUT_DPI`      | 輸出解析度 DPI（預設為 300，降低可減少檔案大小） | `150`            |

## 📊 輸出結果

程式會在終端顯示如下資訊：

- 原始 PDF 頁數與尺寸
- 每頁切割後的 A4 頁面資訊
- 新的頁面順序
- 壓縮前後的檔案大小比較與壓縮率

## 📁 範例輸出檔案

```
輸出檔案：output.pdf
總共輸出頁數：6 張 A4
壓縮率：約 40%
```

---

## 備註

此工具適用於：

- 三折式文宣拆分列印
- 封面裁切出血處理
- 高解析輸出轉成壓縮版發送

## 📝 授權

本專案採用 [MIT License](LICENSE) 授權。
