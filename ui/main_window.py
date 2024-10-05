import random
import sys
import time
from urllib.parse import urlparse

from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, \
    QListWidget, QGridLayout, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox

from core.history_manager import HistoryManager  # 历史管理模块
from crawler.adapted_parsing_methods.manager import *  # 爬取策略管理器
from crawler.crawler import WebCrawler  # 爬虫模块


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

        self.paused = False
        self.stopped = False

    def run(self):
        while self.queue and not self.stopped:
            if self.paused:
                time.sleep(1)
                continue
            address = self.queue.pop(0)
            self.update_log.emit(f"开始爬取 {address}...")
            print(f"正在爬取 {address}...")
            link = address[1]
            link_type = address[2]
            print(f"link_type: {link_type}, link: {link}")


            # 模拟网络延迟 1 到 5 秒
            if random.random() < 0.9:
                delay = random.uniform(2.0, 5.0)
            else:
                delay = random.uniform(5.0, 10.0)
            self.update_log.emit(f"爬取 {link}，等待 {delay} 秒...")
            time.sleep(delay)

            # 获取域名并找到对应的爬取策略
            domain = urlparse(link).netloc
            strategy = self.strategy_manager.get_strategy(domain)

            if strategy:
                parsed_type, parsed_data = strategy(link, link_type)
                if not parsed_data:
                    self.update_completed.emit(f"成功: {link}，但没有找到有效数据。")
                    continue
                elif parsed_type == "url_list":
                    if not parsed_data:
                        self.update_completed.emit(f"成功: {link}，但没有找到有效链接。")
                        continue
                    self.new_queue.emit(parsed_data)
                    self.update_completed.emit(f"成功解析: {link} ，发现 {len(parsed_data)} 个链接。")
                    time.sleep(1)
                    self.update_queue.emit(self.queue)
                elif parsed_type == "file_list":
                    self.update_completed.emit(f"成功解析: {link} ，发现 {len(parsed_data)} 个文件。")
                elif parsed_type == "text":
                    self.update_completed.emit(f"成功: {link}， 数据存储于 {parsed_data}。")
                else:
                    self.update_completed.emit(f"成功: {link}，但没有找到对应的爬取策略。")
            else:
                self.update_failed.emit(f"失败: {link}")

            # 更新待爬取队列

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.stopped = True


class WebCrawlerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.queue = []  # 待爬取队列
        self.initUI()
        self.crawler = WebCrawler()
        self.history_manager = HistoryManager()

        self.crawler_thread = None
        self.strategy_manager = CrawlStrategyManager()

    def initUI(self):
        # 主布局
        self.setWindowTitle('爬虫软件')
        self.setGeometry(100, 100, 1400, 1000)
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

        # 停止按钮
        self.stop_button = QPushButton('停止')
        self.stop_button.clicked.connect(self.stop_crawling)
        url_layout.addWidget(self.stop_button)

        # 暂停按钮
        self.pause_button = QPushButton('暂停')
        self.pause_button.clicked.connect(self.pause_crawling)
        url_layout.addWidget(self.pause_button)

        # 定时器，用于定时询问是否继续运行
        self.pause_timer = QTimer()
        # self.pause_timer.setInterval(3600 * 1000)  # 设置1小时（3600秒）
        self.pause_timer.setInterval(1 * 1000)  # 设置10秒
        self.pause_timer.timeout.connect(self.ask_resume_or_stop)

        # 创建四个区域的控件
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("日志区域")

        self.queue_list = QTableWidget()
        self.queue_list.setRowCount(len(self.queue) + 1)
        self.queue_list.setColumnCount(2)
        self.queue_list.setHorizontalHeaderLabels(["链接", "类型"])
        self.queue_list.setColumnWidth(0, 500)
        self.queue_list.setEditTriggers(QTableWidget.NoEditTriggers)


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

        # 获取页面内容
        status, html = self.crawler.fetch(url, "html")
        if not html:
            self.log_display.setText("获取页面内容失败。")
            return

        # 提取所有链接
        links = [(1, url, "html")]
        self.queue.extend(links)

        # 更新待爬取队列显示
        for link in self.queue:
            new_row_index = 1
            self.queue_list.insertRow(new_row_index)
            self.queue_list.setItem(new_row_index, 0, QTableWidgetItem(link[1]))
            self.queue_list.setItem(new_row_index, 1, QTableWidgetItem(link[2]))

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
        # self.queue_list.clear()
        for link in queue:
            new_row_index = self.queue_list.rowCount() - 1
            self.queue_list.insertRow(new_row_index)
            self.queue_list.setItem(new_row_index, 0, QTableWidgetItem(link[1]))
            self.queue_list.setItem(new_row_index, 1, QTableWidgetItem(link[2]))

    def open_current_folder(self):
        # 打开当前脚本所在的文件夹
        current_folder = os.path.dirname(os.path.abspath(__file__))
        os.startfile(current_folder)  # 在 Windows 上使用 os.startfile() 打开文件夹

    def add_queue_list(self,new_queue_list):

        for link in new_queue_list:
            if link not in self.queue:
                self.queue.append(link)
            elif link in self.queue_list:
                pass

    def stop_crawling(self):
        if self.crawler_thread and self.crawler_thread.isRunning():
            self.crawler_thread.stop()
            self.crawler_thread.wait()  # 等待线程安全结束
            self.log_display.append("爬虫线程已停止。")

    def pause_crawling(self):
        if self.crawler_thread and self.crawler_thread.isRunning():
            if self.crawler_thread.paused:
                self.crawler_thread.resume()
                self.log_display.append("爬虫线程已恢复运行。")
                self.pause_button.setText('暂停')
            else:
                self.crawler_thread.terminate()
                self.pause_timer.start()
                self.log_display.append("爬虫线程已暂停。")
                self.crawler_thread.pause()
                self.pause_button.setText('继续')

    def ask_resume_or_stop(self):
        # 停止计时器，防止重复触发
        self.pause_timer.stop()

        # 创建带有多个选项的对话框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("暂停超时提醒")
        msg_box.setText("暂停时间已超过1小时，请选择操作：")
        pause_button = msg_box.addButton("继续暂停", QMessageBox.ActionRole)
        resume_button = msg_box.addButton("继续爬取", QMessageBox.ActionRole)
        ignore_button = msg_box.addButton("忽略提醒", QMessageBox.ActionRole)
        stop_button = msg_box.addButton("关闭爬虫", QMessageBox.ActionRole)

        # 显示对话框并等待用户选择
        msg_box.exec_()

        if msg_box.clickedButton() == pause_button:
            # 继续暂停，重新启动计时器
            self.pause_timer.start()
            self.log_display.append("继续暂停")
        elif msg_box.clickedButton() == resume_button:
            # 继续爬取
            self.start_crawling()
            self.log_display.append("继续爬取")
        elif msg_box.clickedButton() == ignore_button:
            # 忽略提醒，什么也不做
            self.log_display.append("忽略提醒")
        elif msg_box.clickedButton() == stop_button:
            # 关闭爬虫
            self.stop_crawling()
            self.log_display.append("爬虫已停止")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WebCrawlerApp()
    window.show()
    sys.exit(app.exec_())
