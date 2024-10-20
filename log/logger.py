import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

from config import *

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def __init__(self):
        log_path = LOG_PATH

    def _initialize(self):
        self.logger = logging.getLogger('run')
        self.logger.setLevel(logging.DEBUG)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # 文件处理器，按天分割
        log_name = datetime.datetime.now().strftime('%Y%m%d') + '.log'
        log_path = os.path.join(LOG_PATH, log_name)

        file_handler = TimedRotatingFileHandler(log_path, when='midnight', interval=1, backupCount=7,encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(filename)s - %(lineno)d - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

# 使用示例
if __name__ == '__main__':
    log = Logger().get_logger()
    log.debug('This is a debug message')
    log.info('This is an info message')
    log.warning('This is a warning message')
    log.error('This is an error message')
    log.critical('This is a critical message')
