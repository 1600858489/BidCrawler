import sys
import os
import random
import time
from urllib.parse import urlparse

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, \
    QListWidget, QGridLayout, QComboBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from crawler.crawler import WebCrawler  # 爬虫模块
from crawler.adapted_parsing_methods.manager import *  # 爬取策略管理器
from core.algorithm import filter_file_links  # 筛选算法模块
from core.history_manager import HistoryManager  # 历史管理模块


class CrawlerThread(QThread):
    update_log = pyqtSignal(str)
    update_completed = pyqtSignal(str)
    update_failed = pyqtSignal(str)
    update_queue = pyqtSignal(list)
    new_queue = pyqtSignal(list)

    def __init__(self, queue, crawler, strategy_manager):
        super().__init__()
        self.queue = queue
        self.crawler = crawler
        self.strategy_manager = strategy_manager
        # 初始化爬取策略管理器

    def run(self):
        while self.queue:
            link = self.queue.pop(0)
            # 模拟网络延迟 1 到 5 秒
            delay = random.randint(1, 5)
            self.update_log.emit(f"爬取 {link}，等待 {delay} 秒...")
            time.sleep(delay)

            # 进行爬取
            success, html = self.crawler.fetch(link, level=2)
            print(f"success: {success}, html: {html}")
            if success:
                # 获取域名并找到对应的爬取策略
                domain = urlparse(link).netloc
                strategy = self.strategy_manager.get_strategy(domain)

                if strategy:
                    parsed_data = strategy(link,level=2)
                    print(parsed_data)
                    # for new_link in parsed_data:
                    #     print(new_link)
                    self.new_queue.emit(parsed_data)
                    self.update_completed.emit(f"成功解析: {link} -> {parsed_data}")
                else:
                    self.update_completed.emit(f"成功: {link}，但没有找到对应的爬取策略。")
            else:
                self.update_failed.emit(f"失败: {link}")

            # 更新待爬取队列
            self.update_queue.emit(self.queue)


class WebCrawlerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.crawler = WebCrawler()
        self.history_manager = HistoryManager()
        self.queue = []  # 待爬取队列
        self.crawler_thread = None
        self.strategy_manager = CrawlStrategyManager()

    def initUI(self):
        # 主布局
        self.setWindowTitle('爬虫软件')
        self.setGeometry(100, 100, 800, 600)
        layout = QGridLayout()

        # 输入 URL 区域
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('请输入要爬取的 URL...')
        url_layout.addWidget(self.url_input)

        # 网站选择下拉框
        self.website_combo = QComboBox()
        self.website_combo.addItems([
            "ggzy.qz.gov.cn",
            "ggzyjy.jinhua.gov.cn",
            "ggzy.hzctc.hangzhou.gov.cn",
            "ggzyjy-eweb.wenzhou.gov.cn",
            "jxszwsjb.jiaxing.gov.cn",
            "ggzyjy.huzhou.gov.cn"
        ])
        url_layout.addWidget(self.website_combo)

        # 开始按钮
        self.start_button = QPushButton('开始')
        self.start_button.clicked.connect(self.start_crawling)
        url_layout.addWidget(self.start_button)

        # 打开当前文件夹按钮
        self.open_folder_button = QPushButton('打开当前文件夹')
        self.open_folder_button.clicked.connect(self.open_current_folder)
        url_layout.addWidget(self.open_folder_button)

        # 创建四个区域的控件
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("日志区域")

        self.queue_list = QListWidget()
        self.queue_list.addItem("待爬取队列：")  # 添加默认提示项

        self.completed_list = QListWidget()
        self.completed_list.addItem("已经爬取任务：")  # 添加默认提示项

        self.failed_list = QListWidget()
        self.failed_list.addItem("失败任务：")  # 添加默认提示项

        # 添加 URL 输入区域到布局的顶部
        layout.addLayout(url_layout, 0, 0, 1, 2)

        # 添加四个区域
        layout.addWidget(self.log_display, 1, 0, 1, 2)  # 日志区域占据上半部分
        layout.addWidget(self.queue_list, 2, 0)         # 待爬取队列占据左下
        layout.addWidget(self.completed_list, 2, 1)     # 已经爬取任务占据右下
        layout.addWidget(self.failed_list, 3, 0, 1, 2)  # 失败任务占据最底部

        self.setLayout(layout)

    def start_crawling(self):
        url = self.url_input.text().strip()
        domain = self.website_combo.currentText()

        if not url and not domain:
            self.log_display.setText("请输入有效的 URL。")
            return
        elif not url and domain:
            url = f"http://{domain}/"
        # 检查历史记录中是否已有该 URL
        if self.history_manager.is_in_history(url):
            self.log_display.setText("该 URL 已经爬取过，跳过爬取。")
            return

        # 获取页面内容
        status, html = self.crawler.fetch(url, level=1)
        if not html:
            self.log_display.setText("获取页面内容失败。")
            return
        # 提取所有链接
        links = [url[:-1] + i for i in self.crawler.extract_links(html)]
        file_links = links
        self.queue.extend(file_links)

        if not file_links:
            self.log_display.setText("未找到任何文件链接。")
        else:
            self.log_display.setText("已找到文件链接，开始逐个爬取。")

            # 更新待爬取队列显示
            self.queue_list.clear()
            self.queue_list.addItem("待爬取队列：")
            for link in self.queue:
                self.queue_list.addItem(link)

            # 创建并启动爬虫线程
            self.crawler_thread = CrawlerThread(self.queue, self.crawler, self.strategy_manager)
            self.crawler_thread.update_log.connect(self.update_log_display)
            self.crawler_thread.update_completed.connect(self.update_completed_list)
            self.crawler_thread.update_failed.connect(self.update_failed_list)
            self.crawler_thread.update_queue.connect(self.update_queue_list)
            self.crawler_thread.new_queue.connect(self.add_queue_list)
            self.crawler_thread.start()

        # 添加到历史记录
        self.history_manager.add_to_history(url)

    def update_log_display(self, message):
        """
        更新日志显示
        :param message:
        :return:
        """
        self.log_display.append(message)

    def update_completed_list(self, message):
        """
        更新已经爬取任务列表
        :param message:
        :return:
        """
        self.completed_list.addItem(message)

    def update_failed_list(self, message):
        """
        更新失败任务列表
        :param message:
        :return:
        """
        self.failed_list.addItem(message)

    def update_queue_list(self, queue):
        """
        更新待爬取队列列表
        :param queue:
        :return:
        """
        self.queue_list.clear()
        self.queue_list.addItem("待爬取队列：")
        for link in queue:
            self.queue_list.addItem(link)

    def open_current_folder(self):
        # 打开当前脚本所在的文件夹
        current_folder = os.path.dirname(os.path.abspath(__file__))
        os.startfile(current_folder)  # 在 Windows 上使用 os.startfile() 打开文件夹

    def add_queue_list(self,new_queue_list):
        for link in new_queue_list:
            if link not in self.queue:
                self.queue.append(link)
                self.queue_list.addItem(link)
            elif link in self.queue_list:
                pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WebCrawlerApp()
    window.show()
    sys.exit(app.exec_())
