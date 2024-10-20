import os
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextEdit, QPushButton

from log.logger import Logger
from ui.main_window import WebCrawlerApp

log = Logger().get_logger()

# 路径用于记录是否第一次打开
disclaimer_file = 'disclaimer_accepted.txt'

class DisclaimerDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("免责声明")
        self.resize(1000, 800)

        # 创建布局
        layout = QVBoxLayout(self)

        # 创建 QTextEdit 用于显示免责声明内容（HTML 格式化的文本）
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)  # 设置为只读
        disclaimer_text = """
        <h2>免责声明</h2>
        <p>使用须知：</p>
        <ol>
            <li>本软件“BidCrawler”是为学习与交流网络抓取技术而开发，使用本软件仅限于合法的学习、研究和技术探讨目的。</li>
            <li>本软件仅为工具，开发者不对用户的使用方式承担任何责任。用户需自行了解并遵守相关法律法规，确保所进行的任何操作和行为均符合所在地区的法律规定。</li>
            <li>使用本软件抓取任何公开或私人网站时，用户需遵守该网站的服务条款与使用规则。若违反任何服务条款或法律规定，用户须自行承担全部责任。</li>
            <li>开发者明确禁止用户将本软件用于任何非法、未经授权的网络爬取活动。包括但不限于以下行为：
                <ul>
                    <li>未经授权获取网站上的数据或信息；</li>
                    <li>用于侵犯他人隐私、商业机密或知识产权的行为；</li>
                    <li>参与或协助网络犯罪、欺诈等违法行为。</li>
                </ul>
            </li>
            <li>使用本软件即表示用户已阅读并同意本免责声明。若因违反本免责声明的规定导致的任何法律责任或损失，开发者不承担任何直接或间接的责任。</li>
            <li>开发者保留在任何时间修改或更新本免责声明的权利，用户需自行定期查阅并遵守最新条款。</li>
        </ol>
        """
        self.text_edit.setHtml(disclaimer_text)
        layout.addWidget(self.text_edit)

        # 创建确认按钮
        self.accept_button = QPushButton("我已阅读并同意", self)
        self.accept_button.clicked.connect(self.accept)
        layout.addWidget(self.accept_button)

def show_disclaimer():
    dialog = DisclaimerDialog()
    if dialog.exec_() == QDialog.Accepted:
        return True
    return False

# 检查是否已经显示过免责声明
def check_disclaimer():
    if not os.path.exists(disclaimer_file):
        if show_disclaimer():
            # 创建文件，表示已经阅读过免责声明
            with open(disclaimer_file, 'w') as f:
                f.write('Accepted')  # 记录用户同意的状态
        else:
            # 用户未同意免责声明，退出程序
            sys.exit()

if __name__ == '__main__':
    log.info("Starting Web Crawler App")
    log.info("Python version: " + sys.version)
    log.info("system: " + sys.platform)

    # 初始化 QApplication
    app = QApplication(sys.argv)

    # 检查免责声明
    check_disclaimer()

    # 启动主窗口
    window = WebCrawlerApp()
    window.show()

    # 进入事件循环
    sys.exit(app.exec_())
