from docx import Document
from win32com import client as wc


def read_docx(file_path):
    doc = Document(file_path)
    text = []

    for paragraph in doc.paragraphs:
        text.append(paragraph.text)

    return '\n'.join(text)


def doSaveAs(file_path):
    try:
        word = wc.Dispatch("Word.Application")
        word.Visible = False

        doc = word.Documents.Open(file_path)

        new_file_path = file_path.replace(".doc", ".docx")

        doc.SaveAs(new_file_path, 16)  # 16表示docx格式

        doc.Close()
        word.Quit()
        return new_file_path
    except Exception as e:
        print(e)
        return None


def read_doc(file_path):
    word = wc.Dispatch("Word.Application")
    doc = word.Documents.Open(file_path)
    text = doc.Content.Text
    doc.Close()
    word.Quit()

    return text


if __name__ == '__main__':
    # # 使用示例
    # file_path = "875ec190-2668-4df3-a251-a8de3317b7b5.docx"
    # print(read_docx(file_path))

    # # 使用示例
    file_path = r"F:\python_projcet\BidCrawler\core\file_read\ee.doc"
    print(doSaveAs(file_path))
    # print(read_doc(file_path))
