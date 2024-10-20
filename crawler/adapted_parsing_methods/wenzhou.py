import datetime
import os
import re
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from html2text import html2text

from core.history_manager import HistoryManager
from log.logger import Logger
from .manager import AbstractWebCrawler
from .qz import QzParser

log = Logger().get_logger()

history_manager = HistoryManager()

class WenzhouParser(QzParser):
    """
    WenzhouParser inherits from QzParser and implements its own parsing methods for Wenzhou.
    url: http://ggzyjy-eweb.wenzhou.gov.cn/
    """
    def parse_html(self):
        target_div = self.html_content.find('div', {'class': 'classic-tab'})
        res = []
        for item in target_div.find_all('a'):
            url = self.scheme + '://' + self.domain + item.get('href')
            if "col" not in url:
                continue
            res.append((1, url, "table"))

        self.response_type = "url_list"
        self.response = res

    def parse_table(self):
        script_tag = self.html_content.find_all("script",language="javascript")[2]
        script_content = script_tag.string
        urls = re.findall(r"urls\[i\]='(.*?)';", script_content)
        title = re.findall(r"headers\[i\]='(.*?)';", script_content)
        data_list = []
        for url in urls:
            url = self.scheme + '://' + self.domain + url
            if self.not_in_time(url):
                continue
            if history_manager.is_in_history(url):
                continue
            if self.keyword and self.keyword not in title:
                continue

            data_list.append((1, url, "detail_page"))



        self.response_type = "url_list"
        self.response = data_list

    def get_file_info(self):
        file_info = self.html_content.find_all('a',href=True)
        res = [i for i in file_info if "cmd=download" in i.get('href')]
        return res

    def get_content(self):
        content = self.html_content.find('div',class_='ewb-article')
        if not content:
            content = ""
        content = html2text(str(content))
        return content

    def save_announcement(self,file_path):
        pass