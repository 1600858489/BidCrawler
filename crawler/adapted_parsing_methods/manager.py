from abc import ABC, abstractmethod

import requests

from config import *


class CrawlStrategyManager:
    def __init__(self):
        self.strategies = {
            "ggzy.qz.gov.cn": fetch_ggzy_qz,
            "ggzyjy.jinhua.gov.cn": fetch_ggzyjy_jinhua,
            "ggzy.hangzhou.gov.cn": fetch_ggzy_hangzhou,
            "ggzyjyeweb.wenzhou.gov.cn": fetch_ggzyjyeweb_wenzhou,
            "jxszwsjb.jiaxing.gov.cn": fetch_jxszwsjb_jiaxing,
            "ggzyjy.huzhou.gov.cn": fetch_ggzyjy_huzhou
        }

    def register_strategy(self, domain, strategy_function):
        """注册一个域名和对应的爬取策略"""
        self.strategies[domain] = strategy_function

    def get_strategy(self, domain):
        """获取指定域名的爬取策略"""
        print(f"  Getting strategy for domain: {domain}")
        return self.strategies.get(domain, None)


# 示例爬取策略
def fetch_ggzy_qz(url, link_type):
    print(url, link_type)
    # 针对 ggzy.qz.gov.cn 的爬取策略
    from crawler.adapted_parsing_methods.qz import QzParser
    parser = QzParser(
        url=url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",

        }

    )

    if link_type == "html":
        parser.url_type = "html"
        parser.run()
        if parser.response_type == "url_list":
            return "url_list", parser.response
        elif parser.response_type == "html":
            return "html", parser.html_content
    elif link_type == "table":
        parser.url_type = "table"
        print("  Fetching table data...")

        parser.run()
        if parser.response_type == "url_list":
            return "url_list", parser.response
        elif parser.response_type == "html":
            return "html", parser.html_content
        elif parser.response_type == "json":
            return "json", parser.response
    elif link_type == "detail_page":
        parser.url_type = "detail_page"
        parser.run()
        if parser.response_type == "url_list":
            return "url_list", parser.response
        elif parser.response_type == "html":
            return "html", parser.html_content
        elif parser.response_type == "json":
            return "json", parser.response
        else:
            return "text", parser.response




def fetch_ggzyjy_jinhua(url):
    # 针对 ggzyjy.jinhua.gov.cn 的爬取策略
    return f"Fetched data from ggzyjy.jinhua.gov.cn: {url[:100]}"


def fetch_ggzy_hangzhou(html_content):
    # 针对 ggzy.hangzhou.gov.cn 的爬取策略
    return f"Fetched data from ggzy.hangzhou.gov.cn: {html_content[:100]}"


def fetch_ggzyjyeweb_wenzhou(html_content):
    # 针对 ggzyjyeweb.wenzhou.gov.cn 的爬取策略
    return f"Fetched data from ggzyjyeweb.wenzhou.gov.cn: {html_content[:100]}"


def fetch_jxszwsjb_jiaxing(html_content):
    # 针对 jxszwsjb.jiaxing.gov.cn 的爬取策略
    return f"Fetched data from jxszwsjb.jiaxing.gov.cn: {html_content[:100]}"


def fetch_ggzyjy_huzhou(html_content):
    # 针对 ggzyjy.huzhou.gov.cn 的爬取策略
    return f"Fetched data from ggzyjy.huzhou.gov.cn: {html_content[:100]}"


class AbstractWebCrawler(ABC):
    def __init__(self, url, headers=None, params=None, proxies=None, data=None, method="GET", max_page=10):
        """
        初始化网页爬虫的基础属性。
        :param url: 爬取目标 URL
        :param headers: HTTP 请求头
        :param params: URL 参数（GET 请求）
        :param proxies: 代理配置
        :param data: 请求体数据（用于 POST 请求）
        :param method: HTTP 方法，默认为 "GET"
        """
        self.url = url
        self.url_type = ""
        self.headers = headers or {}
        self.params = params or {}
        self.proxies = proxies or {}
        self.data = data or {}
        self.method = method.upper()
        self.html_content = None
        self.session = requests.Session()
        # 响应类型
        """
        text: 纯文本数据
        table: 表格数据
        detail_page: 详情页数据
        url_list: 网页中包含的 URL 列表
        json: JSON 数据
        binary: 二进制数据
        file: 文件下载
        control: 控制信息
        """
        self.response_type = ""
        self.response = None
        self.file_path = FILE_PATH
        self.max_page = max_page


    @abstractmethod
    def fetch(self):
        """
        获取网页内容。子类需实现该方法来从指定的 URL 下载网页内容。
        """
        pass

    @abstractmethod
    def parse(self):
        """
        解析网页内容。子类需实现该方法以提取所需的数据。
        """
        pass

    def run(self):
        """
        运行整个爬虫过程：获取内容 -> 解析。
        """
        if not self.url:
            raise ValueError("URL不能为空。")
        self.fetch()
        if self.html_content is not None:
            self.parse()
