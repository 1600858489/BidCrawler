import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.uic.properties import QtCore

from ui.main_window import WebCrawlerApp
from log.logger import Logger

log = Logger().get_logger()

if __name__ == '__main__':
    log.info("Starting Web Crawler App")
    log.info("Python version: " + sys.version)
    log.info("system: "+ sys.platform)

    app = QApplication(sys.argv)
    window = WebCrawlerApp()
    window.show()
    sys.exit(app.exec_())

