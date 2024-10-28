from docx import Document
from win32com import client as wc


def read_and_convert_doc(file_path):
    try:
        # 检查文件扩展名，若是.doc文件，则先转换为.docx格式
        if file_path.endswith('.doc'):
            word = wc.Dispatch("Word.Application")
            word.Visible = False
            doc = word.Documents.Open(file_path)
            new_file_path = file_path.replace(".doc", ".docx")
            doc.SaveAs(new_file_path, 16)  # 16表示docx格式
            doc.Close()
            word.Quit()
            file_path = new_file_path  # 更新文件路径为新生成的.docx文件

        # 读取.docx文件内容
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)

        return '\n'.join(text)

    except Exception as e:
        print(e)
        return None
