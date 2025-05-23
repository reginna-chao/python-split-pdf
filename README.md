# 📄 Split PDF with Python

A tool for splitting wide-format PDFs into tri-fold A4-sized pages, supporting:
- Bleed trimming
- Custom page order
- Image and PDF structure compression to reduce output file size

## 🌐 Languages

- [English](README.md)
- [繁體中文](docs/README.zh-TW.md)

---

## 🧩 Features

- ✂️ Split each wide-format PDF page into three A4 pages
- 🩸 Support for bleed area trimming
- 🔢 Customizable output page order (e.g., for booklet printing)
- 🗜️ JPEG image compression and PDF optimization
- 📐 Adjustable output resolution (DPI) to further reduce file size

---

## 📦 Requirements

Please install the following packages first:

```bash
pip install pymupdf python-dotenv
```

## 🚀 Usage

1. Create a `.env` configuration file  
Example `.env` file:

```
# Bleed setting (unit: mm)
PRINT_BLEED=2

# Output page order (comma-separated, starting from 1)
PAGE_ORDER=3,4,1,5,6,2

# Enable image compression
COMPRESS_IMAGES=true

# JPEG compression quality (0~100)
IMAGE_QUALITY=85

# Enable PDF structure compression
COMPRESS_PDF=true

# Output DPI (e.g., 150 lowers resolution to compress file size)
OUTPUT_DPI=150
```

2. Run the command

```bash
python split_pdf.py input.pdf output.pdf
```

### ⚙️ Environment Variable Descriptions
| Variable Name         | Description                                      | Example Value      |
| --------------------- | ------------------------------------------------ | ------------------ |
| `PRINT_BLEED`         | Bleed setting (trimmed edge, unit: mm)           | `2`                |
| `PAGE_ORDER`          | Output page order (comma-separated, start from 1) | `3,4,1,5,6,2`      |
| `COMPRESS_IMAGES`     | Enable image compression                         | `true` / `false`   |
| `IMAGE_QUALITY`       | JPEG compression quality (0~100)                 | `85`               |
| `COMPRESS_PDF`        | Enable PDF structure compression                 | `true` / `false`   |
| `OUTPUT_DPI`          | Output resolution DPI (default 300, lower to reduce file size) | `150`  |

## 📊 Output

The program will display the following information in the terminal:

- Original PDF page count and size
- A4 page info after splitting each page
- New page order
- File size comparison and compression rate before and after compression

## 📁 Example Output

```
Output file: output.pdf
Total output pages: 6 A4 pages
Compression rate: about 40%
```

---

## Notes

This tool is suitable for:

- Tri-fold brochure splitting and printing
- Cover bleed trimming
- Converting high-resolution output to compressed versions for distribution

## 📝 License

This project is licensed under the [MIT License](LICENSE).
