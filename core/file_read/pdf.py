from PyPDF2 import PdfReader


def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ''
    for page in range(len(reader.pages)):
        # 处理每一页的内容
        text += reader.pages[page].extract_text()

    print(text)
    return text


if __name__ == '__main__':
    file_path = '中标结果公告.pdf'
    read_pdf(file_path)
