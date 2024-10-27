import os
from io import BytesIO

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"D:\Tesseract-OCR\tesseract.exe"  # 替换为你的 Tesseract 安装路径

os.environ["TESSDATA_PREFIX"] = r"D:\Tesseract-OCR\tessdata"  # 替换为你的 Tesseract 数据路径


def ocr_image(image: Image.Image, lang="eng") -> str:
    """
    对传入的 PIL 图像进行 OCR 并返回提取的文本内容。

    参数:
        image (Image.Image): 要进行 OCR 处理的 PIL 图像对象。
        lang (str): OCR 语言，默认为 "eng"。

    返回:
        str: 提取的文本内容。
    """
    return pytesseract.image_to_string(image, lang=lang)


def ocr_images_from_pdf(pdf_path: str, lang="eng"):
    """
    从 PDF 文件中提取图片并进行 OCR 识别。

    参数:
        pdf_path (str): PDF 文件的路径。
        lang (str): OCR 语言，默认为 "eng"。

    返回:
        dict: 包含页码和 OCR 文本内容的字典。
    """
    pdf_document = fitz.open(pdf_path)
    ocr_results = {}

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        images = page.get_images(full=True)

        for image_index, image in enumerate(images):
            xref = image[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]

            # 将图片字节转换为 PIL 图像
            pil_image = Image.open(BytesIO(image_bytes))

            # 对图像进行 OCR
            text = ocr_image(pil_image, lang=lang)
            key = f"Page {page_number + 1} - Image {image_index + 1}"
            ocr_results[key] = text
            print(f"{key} OCR Text:")
            print(text)
            print("-" * 50)

    pdf_document.close()
    return ocr_results
