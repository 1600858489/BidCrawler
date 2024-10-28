import base64
from io import BytesIO

from pdf2image import convert_from_path

from config import *
from log.logger import Logger

log = Logger().get_logger()


def read_pdf(pdf_path) -> list[str]:
    """
    提取 PDF 中的文字和图片，图片进行 Base64 编码
    """
    base64_images = []
    poppler_path = os.path.join(BASE_DIR, 'poppler-24.08.0/Library/bin')
    # 打开 PDF 文件并提取文字

    # 将 PDF 页面转换为图像
    images = convert_from_path(pdf_path, poppler_path=poppler_path)

    # 遍历每一页图像并进行 Base64 编码
    for img in images:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        base64_images.append(img_base64)
    log.info(f"PDF 页面转换为图像成功，共 {len(images)} 页")
    return base64_images




if __name__ == '__main__':
    file_path = '中标结果公告.pdf'
    read_pdf(file_path)
