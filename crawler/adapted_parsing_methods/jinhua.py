import datetime
import os
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup

from core.history_manager import HistoryManager
from .manager import AbstractWebCrawler
from log.logger import Logger

log = Logger().get_logger()

history_manager = HistoryManager()

class JinhuaParser(AbstractWebCrawler):


    def fetch(self):
        log.info(f"Fetching {self.url}")
        headers = self.headers

        try:
            response = self.session.get(self.url, headers=headers)
            if response.status_code == 200:
                log.info(f"Fetch successful for {self.url}")
                log.info(f"response content: {response.status_code}")
                self.html_content = BeautifulSoup(response.content, 'html.parser')
            else:
                log.error(f"Fetch failed for {self.url}")
                log.error(f"response status code: {response.status_code}")
                log.error(f"response content: {response.content}")
                self.html_content = None
        except Exception as e:
            log.error(f"Fetch failed for {self.url}")
            log.error(f"Error: {e}")

        try:
            log.info(f"self.session history: {self.session.history[-1].url}")
        except:
            pass

    def parse(self):
        if self.html_content is None:
            return None
        elif self.html_content is not None:
            domain = urlparse(self.url).netloc
            scheme = urlparse(self.url).scheme
            if self.url_type == 'html':
                target_tag = self.html_content.find_all('div', {'class': 'article-content'})
                if target_tag:
                    for tag in target_tag:
            elif self.url_type == 'table':
                pass

            elif self.url_type == 'detail_page':
                pass
