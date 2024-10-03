import re

import requests
from bs4 import BeautifulSoup

from .adapted_parsing_methods.manager import *

class WebCrawler:
    def __init__(self):
        self.crawl_strategy_manager = CrawlStrategyManager()

    def fetch(self, url, level=1):
        if "ggzy.qz.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("ggzy.qz.gov.cn")
        elif "ggzyjy.jinhua.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("ggzyjy.jinhua.gov.cn")
        elif "ggzy.hzctc.hangzhou.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("ggzy.hzctc.hangzhou.gov.cn")
        elif "ggzyjy-eweb.wenzhou.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("ggzyjy-eweb.wenzhou.gov.cn")
        elif "jxszwsjb.jiaxing.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("jxszwsjb.jiaxing.gov.cn")
        elif "ggzyjy.huzhou.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("ggzyjy.huzhou.gov.cn")
        else:
            return False, None
        # 模拟获取页面内容
        res = strategy(url, level)
        if res is None:
            return False, None
        return True, res

    def extract_links(self, html):
        res = []
        target_div = html.select_one('#tab1 > div:nth-child(1) > ul')

        for tag in target_div.select('li'):
            link = tag.get('href')
            res.append(link)
        return res



    def crawl(self, url):
        # 模拟爬取返回 (成功状态, 路径)
        if "file1" in url:
            return True, "/path/to/file1"
        else:
            return False, None
