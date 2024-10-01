import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, \
    QListWidget
from PyQt5.QtCore import Qt
from crawler.crawler import WebCrawler
from core.algorithm import filter_file_links
from core.history_manager import HistoryManager


class WebCrawlerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.crawler = WebCrawler()
        self.history_manager = HistoryManager()

    def initUI(self):
        # 主布局
        self.setWindowTitle('爬虫软件')
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()

        # 输入 URL 区域
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('请输入要爬取的 URL...')
        url_layout.addWidget(self.url_input)

        # 开始按钮
        self.start_button = QPushButton('开始')
        self.start_button.clicked.connect(self.start_crawling)
        url_layout.addWidget(self.start_button)

        layout.addLayout(url_layout)

        # 爬取结果展示
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        # 历史记录区域
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

        self.setLayout(layout)

    def start_crawling(self):
        url = self.url_input.text().strip()
        if not url:
            self.result_display.setText("请输入有效的 URL。")
            return

        # 检查历史记录中是否已有该 URL
        if self.history_manager.is_in_history(url):
            self.result_display.setText("该 URL 已经爬取过，跳过爬取。")
            return

        try:
            # 获取页面内容
            html = self.crawler.fetch(url)
            # 提取所有链接
            links = self.crawler.extract_links(html)
            # 筛选文件链接
            file_links = filter_file_links(links)

            if file_links:
                self.result_display.setText("\n".join(file_links))
            else:
                self.result_display.setText("未找到任何文件链接。")

            # 添加到历史记录
            self.history_manager.add_to_history(url)
            self.history_list.addItem(url)
        except Exception as e:
            self.result_display.setText(str(e))

