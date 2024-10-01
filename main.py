import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import WebCrawlerApp

if __name__ == '__main__':

    with open('config.json', 'w') as f:
        f.write('{}')

    app = QApplication(sys.argv)
    window = WebCrawlerApp()
    window.show()
    sys.exit(app.exec_())

