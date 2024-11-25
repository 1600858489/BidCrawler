import base64
from io import BytesIO

import pdfplumber
from pdf2image import convert_from_path

from config import *
from log.logger import Logger

log = Logger().get_logger()


def get_base64(img) -> str:
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_base64


def read_pdf(pdf_path, poppler_path=None) -> tuple[str, list[str]]:
    """
    提取 PDF 中的文字和图片，图片进行 Base64 编码
    """
    base64_images = []

    if not poppler_path:
        poppler_path = os.path.join(BASE_DIR, 'poppler/Library/bin')
    # 打开 PDF 文件并提取文字和表格
    text_content = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_content += page.extract_text() + "\n"

    # print(text_content)
    # 将 PDF 页面转换为图像
    images = convert_from_path(pdf_path, poppler_path=poppler_path)

    # 遍历每一页图像并进行 Base64 编码
    if text_content == "" or len(text_content) <= 50:
        for img in images:
            base64_images.append(get_base64(img))
        log.info(f"PDF 页面转换为图像成功，共 {len(images)} 页")
    return text_content, base64_images




if __name__ == '__main__':
    file_path = r'F:\python_projcet\BidCrawler\core\bot\20241124035011c0bf96.pdf'
    read_pdf(file_path, poppler_path=r'F:\python_projcet\BidCrawler\poppler\Library\bin')
