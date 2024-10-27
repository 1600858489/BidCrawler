import random
import sys
import time
from urllib.parse import urlparse

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, \
    QListWidget, QGridLayout, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QVBoxLayout, QSpinBox, QLabel

from core.history_manager import HistoryManager  # 历史管理模块
from crawler.adapted_parsing_methods.manager import *  # 查询策略管理器
from crawler.crawler import WebCrawler  # 查询工具模块
from log.logger import Logger

log = Logger().get_logger()


class CrawlerThread(QThread):
    update_log = pyqtSignal(str)
    update_completed = pyqtSignal(str)
    update_failed = pyqtSignal(str)
    update_queue = pyqtSignal(list)
    new_queue = pyqtSignal(list)

    def __init__(self, queue, crawler, strategy_manager, key_words, max_day, api_key, api_base, large_model,
                 enable_delay):
        """
        初始化查询线程
        :param queue: 待查询队列
        :param crawler: 查询工具模块
        :param strategy_manager: 查询策略管理器
        :param key_words: 查询关键词
        :param max_day: 最大查询天数
        :param api_key: 百度API Key
        :param api_base: 百度API Base
        :param large_model: 是否使用大模型
        :param enable_delay: 是否启用延迟
        """
        super().__init__()
        self.queue = queue
        self.crawler = crawler
        self.strategy_manager = strategy_manager
        self.key_words = key_words
        self.max_day = max_day
        # 初始化查询策略管理器

        self.paused = False
        self.stopped = False
        self.api_key = api_key
        self.api_base = api_base
        self.large_model = large_model
        self.enable_delay = enable_delay

    def run(self):
        search_num = 0
        start_time = time.time()
        while self.queue and not self.stopped:
            if self.paused:
                time.sleep(1)
                continue
            address = self.queue.pop(0)
            self.update_log.emit(f"开始查询 {address}...")
            link = address[1]
            link_type = address[2]

            if self.enable_delay:

                # 模拟网络延迟 1 到 5 秒
                if random.random() < 0.9:
                    delay = random.uniform(0.5, 1.5)
                else:
                    delay = random.uniform(2.0, 4.0)
                self.update_log.emit(f"查询 {link}，等待 {delay} 秒...")
                time.sleep(delay)
            else:
                self.update_log.emit(f"查询 {link}...")


            # 获取域名并找到对应的查询策略
            domain = urlparse(link).netloc
            strategy = self.strategy_manager.get_strategy(domain)

            if strategy:
                print(f"开始查询 {link}...{self.key_words}")
                resulta = strategy(link, link_type,self.key_words,self.max_day)

                if resulta is None:
                    break
                parsed_type, parsed_data = resulta
                if not parsed_data:
                    # self.update_completed.emit(f"成功: {link}，但没有找到有效数据。尚未记录入历史记录")
                    if parsed_type != "url_list":
                        self.update_failed.emit(f"{link}  查询出现异常，请查看日志。 该条记录尚未记录入历史记录。")
                        log.info(f"session {link} has no valid data")
                    else:
                        self.update_completed.emit(f"成功: {link}，但没有找到有效链接。 请检查条件范围内是否有可寻找数据，以及历史记录是否存在")

                elif parsed_type == "url_list":
                    if not parsed_data:
                        self.update_completed.emit(f"成功: {link}，但没有找到有效链接。 请检查条件范围内是否有可寻找数据，以及历史记录是否存在")
                        log.info(f"session {link} has no valid data")

                    self.new_queue.emit(parsed_data)
                    self.update_completed.emit(f"成功解析: {link} ，发现 {len(parsed_data)} 个链接。")
                    log.info(f"session {link} has {len(parsed_data)} valid links")
                    time.sleep(1)

                elif parsed_type == "file_list":
                    self.update_completed.emit(f"成功解析: {link} ，发现 {len(parsed_data)} 个文件。")
                    log.info(f"session {link} has no valid data")
                elif parsed_type == "text":
                    self.update_completed.emit(f"成功: {link}， 数据存储于 {parsed_data}。")
                    log.info(f"session {link} has no valid data")
                else:
                    self.update_failed.emit(f"失败: {link}，没有找到对应的查询策略。")
                    log.info(f"session {link} has no valid data")
            else:
                self.update_failed.emit(f"失败: {link}，未知错误，请查看日志。")

                log.info(f"session {link} has no valid data")
            self.update_queue.emit(self.queue)
            search_num += 1

            # 更新待查询队列
        end_time = time.time()
        total_seconds = int(end_time - start_time)

        if total_seconds < 60:
            time_display = f"{total_seconds:.2f}秒"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_display = f"{minutes}分钟 {seconds:.2f}秒"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            time_display = f"{hours}小时 {minutes}分钟 {seconds:.2f}秒"
        else:
            days = total_seconds // 86400
            hours = (total_seconds % 86400) // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            time_display = f"{days}天 {hours}小时 {minutes}分钟 {seconds:.2f}秒"

        self.update_log.emit(f"查询完成，共查询 {search_num} 个链接，用时 {time_display}。")



    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.stopped = True


class WebCrawlerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.queue = []  # 待查询队列
        self.initUI()
        self.crawler = WebCrawler()
        self.history_manager = HistoryManager()
        self.key_words = None

        self.crawler_thread = None
        self.strategy_manager = CrawlStrategyManager()

    def initUI(self):

        self.__version__ =  VERSION
        # 主布局
        self.setWindowTitle(f'查询工具软件-{self.__version__}')

        self.setGeometry(100, 100, 1400, 1000)
        layout = QGridLayout()






        # 输入区域布局
        input_layout = QVBoxLayout()

        # 输入 URL 区域
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('请输入要查询的 URL')
        url_layout.addWidget(self.url_input)

        # 网站选择下拉框
        self.website_combo = QComboBox()
        self.website_combo.addItems([
            PLATFORM_HASH["ggzy.qz.gov.cn"],
            PLATFORM_HASH["ggzyjy.jinhua.gov.cn"],
            PLATFORM_HASH["ggzy.hzctc.hangzhou.gov.cn"],
            PLATFORM_HASH["ggzyjy-eweb.wenzhou.gov.cn"],
            PLATFORM_HASH["jxszwsjb.jiaxing.gov.cn"],
            PLATFORM_HASH["ggzyjy.huzhou.gov.cn"],
            PLATFORM_HASH["zsztb.zhoushan.gov.cn"],
            PLATFORM_HASH["ggzy.tzztb.zjtz.gov.cn"],
            PLATFORM_HASH["lssggzy.lishui.gov.cn"]
        ])
        url_layout.addWidget(self.website_combo)

        input_layout.addLayout(url_layout)

        # 输入关键字区域
        keyword_layout = QHBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText('请输入要查询的关键字')
        keyword_layout.addWidget(self.keyword_input)
        input_layout.addLayout(keyword_layout)

        # 输入 API Key 区域
        api_key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText('请输入 API Key')
        api_key_layout.addWidget(self.api_key_input)
        input_layout.addLayout(api_key_layout)

        # 输入 API Base 区域
        api_base_layout = QHBoxLayout()
        self.api_base_input = QLineEdit()
        self.api_base_input.setPlaceholderText('请输入 API Base URL')
        api_base_layout.addWidget(self.api_base_input)
        input_layout.addLayout(api_base_layout)

        # 是否启用大模型选择框
        self.large_model_checkbox = QComboBox()
        self.large_model_checkbox.addItems(['启用大模型', '不启用大模型'])
        input_layout.addWidget(self.large_model_checkbox)

        # 是否启用延迟选择框
        self.enable_delay_checkbox = QComboBox()
        self.enable_delay_checkbox.addItems(['启用延迟', '不启用延迟'])
        input_layout.addWidget(self.enable_delay_checkbox)

        # 创建查询目标日期的输入区域
        date_range_layout = QHBoxLayout()
        self.target_days_input = QSpinBox()  # 使用 QSpinBox 让用户输入天数
        self.target_days_input.setRange(1, 9999)  # 设置可输入的范围，1到365天
        self.target_days_input.setValue(7)  # 设置默认值为1
        date_range_label = QLabel('需要查询')
        date_range_layout.addWidget(date_range_label)  # 标签提示
        date_range_layout.addWidget(self.target_days_input)  # 天数输入框
        date_range_label = QLabel('天内的信息')
        date_range_layout.addWidget(date_range_label)  # 标签提示
        input_layout.addLayout(date_range_layout)

        # 添加输入区域布局到主布局
        layout.addLayout(input_layout, 0, 0, 1, 2)  # 将输入区域放在顶部

        # 操作按钮区域
        button_layout = QHBoxLayout()

        # 开始按钮
        self.start_button = QPushButton('开始')
        self.start_button.clicked.connect(self.start_crawling)
        button_layout.addWidget(self.start_button)

        # 打开当前文件夹按钮
        self.open_folder_button = QPushButton('打开当前文件夹')
        self.open_folder_button.clicked.connect(self.open_current_folder)
        button_layout.addWidget(self.open_folder_button)

        # 停止按钮
        self.stop_button = QPushButton('停止')
        self.stop_button.clicked.connect(self.stop_crawling)
        button_layout.addWidget(self.stop_button)

        # 暂停按钮
        self.pause_button = QPushButton('暂停')
        self.pause_button.clicked.connect(self.pause_crawling)
        button_layout.addWidget(self.pause_button)

        # 将按钮区域添加到主布局
        layout.addLayout(button_layout, 1, 0, 1, 2)  # 按钮区域放在输入区域下方

        # 显示日志区域
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("日志区域")
        layout.addWidget(self.log_display, 2, 0, 1, 2)  # 日志区域占据上半部分

        # 创建待查询队列及已完成、失败任务列表
        self.queue_list = QTableWidget()
        self.queue_list.setRowCount(len(self.queue) + 1)
        self.queue_list.setColumnCount(2)
        self.queue_list.setHorizontalHeaderLabels(["链接", "类型"])
        self.queue_list.setColumnWidth(0, 500)
        self.queue_list.setEditTriggers(QTableWidget.NoEditTriggers)

        self.completed_list = QListWidget()
        self.completed_list.addItem("已经查询任务：")  # 添加默认提示项

        self.failed_list = QListWidget()
        self.failed_list.addItem("失败任务：")  # 添加默认提示项

        layout.addWidget(self.queue_list, 3, 0)  # 待查询队列占据左下
        layout.addWidget(self.completed_list, 3, 1)  # 已经查询任务占据右下
        layout.addWidget(self.failed_list, 4, 0, 1, 2)  # 失败任务占据最底部

        self.setLayout(layout)

    def start_crawling(self):
        url = self.url_input.text().strip()
        domain = self.website_combo.currentText()
        keyword = self.keyword_input.text().strip()
        max_day = self.target_days_input.value()
        api_key = self.api_key_input.text().strip()
        api_base = self.api_base_input.text().strip()
        large_model = self.large_model_checkbox.currentText() == True
        enable_delay = self.enable_delay_checkbox.currentText() == True

        for k, v in PLATFORM_HASH.items():
            if v == domain:
                domain = k
                break
        print(url, domain, keyword, max_day)

        if not url and not domain:
            self.log_display.setText("请输入有效的查询目标 。")
            return
        elif url:
            if "https" in url or "http" in url:
                url = [url]
            else:
                url = ["https://" + i for i in [
            "ggzy.qz.gov.cn",
            "ggzy.hzctc.hangzhou.gov.cn",
            "ggzyjy-eweb.wenzhou.gov.cn",
            "jxszwsjb.jiaxing.gov.cn",
            "ggzyjy.huzhou.gov.cn",
            "ggzy.tzztb.zjtz.gov.cn",
            "lssggzy.lishui.gov.cn"
        ]].extend(["http://"+"zsztb.zhoushan.gov.cn","http://"+"ggzyjy.jinhua.gov.cn"])

        elif not url and domain:
            if domain in ["zsztb.zhoushan.gov.cn","ggzyjy.jinhua.gov.cn",]:
                url = ["http://"+domain]
            else:
                url = [f"https://{domain}/"]

        # 获取页面内容
        for i in url:
            # print(i)
            # status, html = self.crawler.fetch(i, "html")
            # if not html:
            #     self.log_display.setText("获取页面内容失败。")
            #     return

            # 提取所有链接
            links = [(1, i, "html")]
            self.queue.extend(links)

        # 更新待查询队列显示
        for link in self.queue:
            new_row_index = 1
            print(link)
            self.queue_list.insertRow(new_row_index)
            self.queue_list.setItem(new_row_index, 0, QTableWidgetItem(link[1]))
            self.queue_list.setItem(new_row_index, 1, QTableWidgetItem(link[2]))

        # 创建并启动查询工具线程
        self.crawler_thread = CrawlerThread(self.queue, self.crawler, self.strategy_manager, keyword, max_day, api_key,
                                            api_base, large_model, enable_delay)
        self.crawler_thread.update_log.connect(self.update_log_display)
        self.crawler_thread.update_completed.connect(self.update_completed_list)
        self.crawler_thread.update_failed.connect(self.update_failed_list)
        self.crawler_thread.update_queue.connect(self.update_queue_list)
        self.crawler_thread.new_queue.connect(self.add_queue_list)
        self.crawler_thread.start()

    def update_log_display(self, message):
        """
        更新日志显示
        :param message:
        :return:
        """
        self.log_display.append(message)

    def update_completed_list(self, message):
        """
        更新已经查询任务列表
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
        更新待查询队列列表
        :param queue:
        :return:
        """

        header = [self.queue_list.horizontalHeaderItem(i).text() for i in range(self.queue_list.columnCount())]
        self.queue_list.clear()
        self.queue_list.setHorizontalHeaderLabels(header)
        row_count = self.queue_list.rowCount()
        for row in range(row_count - 1, 0, -1):
            self.queue_list.removeRow(row)
        for link in queue:
            new_row_index = self.queue_list.rowCount() - 1
            self.queue_list.insertRow(new_row_index)
            self.queue_list.setItem(new_row_index, 0, QTableWidgetItem(link[1]))
            self.queue_list.setItem(new_row_index, 1, QTableWidgetItem(link[2]))

    def open_current_folder(self):
        # 打开当前脚本所在的文件夹
        from config import FILE_PATH
        os.startfile(FILE_PATH)  # 在 Windows 上使用 os.startfile() 打开文件夹

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
            self.queue = []
            header = [self.queue_list.horizontalHeaderItem(i).text() for i in range(self.queue_list.columnCount())]
            self.queue_list.clear()
            self.queue_list.setHorizontalHeaderLabels(header)
            row_count = self.queue_list.rowCount()
            for row in range(row_count - 1, 0, -1):
                self.queue_list.removeRow(row)
            self.log_display.append("查询工具线程已停止。")

    def pause_crawling(self):
        if self.crawler_thread and self.crawler_thread.isRunning():
            if self.crawler_thread.paused:
                self.crawler_thread.resume()
                self.log_display.append("查询工具线程已恢复运行。")
                self.pause_button.setText('暂停')
            else:
                self.crawler_thread.terminate()
                self.pause_timer.start()
                self.log_display.append("查询工具线程已暂停。")
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
        resume_button = msg_box.addButton("继续查询", QMessageBox.ActionRole)
        ignore_button = msg_box.addButton("忽略提醒", QMessageBox.ActionRole)
        stop_button = msg_box.addButton("关闭查询工具", QMessageBox.ActionRole)

        # 显示对话框并等待用户选择
        msg_box.exec_()

        if msg_box.clickedButton() == pause_button:
            # 继续暂停，重新启动计时器
            self.pause_timer.start()
            self.log_display.append("继续暂停")
        elif msg_box.clickedButton() == resume_button:
            # 继续查询
            self.start_crawling()
            self.log_display.append("继续查询")
        elif msg_box.clickedButton() == ignore_button:
            # 忽略提醒，什么也不做
            self.log_display.append("忽略提醒")
        elif msg_box.clickedButton() == stop_button:
            # 关闭查询工具
            self.stop_crawling()
            self.log_display.append("查询工具已停止")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = WebCrawlerApp()
    window.show()
    sys.exit(app.exec_())
