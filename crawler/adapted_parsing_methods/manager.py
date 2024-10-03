from abc import ABC, abstractmethod

import requests



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
def fetch_ggzy_qz(url, level):
    # 针对 ggzy.qz.gov.cn 的爬取策略
    from crawler.adapted_parsing_methods.qz import QzParser
    parser = QzParser(
        url=url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",

        }

    )
    if level == 1:
        parser.fetch()
    else:
        parser.run()
    res = parser.html_content
    return res


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
    def __init__(self, url, headers=None, params=None, proxies=None, data=None, method="GET"):
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
        self.headers = headers or {}
        self.params = params or {}
        self.proxies = proxies or {}
        self.data = data or {}
        self.method = method.upper()
        self.html_content = None
        self.session = requests.Session()

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
        self.parse()
