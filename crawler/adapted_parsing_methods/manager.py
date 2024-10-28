import json
import traceback
from abc import ABC, abstractmethod

import requests

from config import *
from log.logger import Logger

log = Logger().get_logger()

class CrawlStrategyManager:
    config_file = CONFIG_PATH
    def __init__(self):
        self.strategies = {
            "ggzy.qz.gov.cn": fetch_ggzy_qz,
            "ggzyjy.jinhua.gov.cn": fetch_ggzyjy_jinhua,
            "ggzy.hzctc.hangzhou.gov.cn": fetch_ggzy_hangzhou,
            "ggzyjy-eweb.wenzhou.gov.cn": fetch_ggzyjyeweb_wenzhou,
            "jxszwsjb.jiaxing.gov.cn": fetch_jxszwsjb_jiaxing,
            "ggzyjy.huzhou.gov.cn": fetch_ggzyjy_huzhou,
            "zsztb.zhoushan.gov.cn": fetch_zsztb_zhoushan,
            "ggzy.tzztb.zjtz.gov.cn": fetch_tzztb_zjtz,
            "lssggzy.lishui.gov.cn": fetch_lssggzy_lishui

        }

    @classmethod
    def load_config(cls):
        if os.path.exists(cls.config_file):
            with open(cls.config_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {
            'api_key': '',
            'api_base': ''
        }

    @classmethod
    def save_config(cls, config):
        with open(cls.config_file, 'w', encoding='utf-8') as file:
            json.dump(config, file)

    def register_strategy(self, domain, strategy_function):
        """注册一个域名和对应的查询策略"""
        self.strategies[domain] = strategy_function

    def get_strategy(self, domain):
        """获取指定域名的查询策略"""
        log.info(f"Getting strategy for domain: {domain}")
        return self.strategies.get(domain, None)


def fetch_data(parser, link_type):
    """使用解析器获取数据，减少重复代码"""
    parser.run()
    if parser.response_type == "url_list":
        return "url_list", parser.response
    elif parser.response_type in ["html", "json"]:
        return parser.response_type, parser.html_content if parser.response_type == "html" else parser.response
    else:
        return "text", parser.response


def fetch_ggzy_qz(url, link_type, keyword, max_day, api_key, api_base, large_model):
    from crawler.adapted_parsing_methods.qz import QzParser
    try:
        parser = QzParser(url=url, headers={"User-Agent": "Mozilla/5.0"}, keyword=keyword, max_day=max_day,
                          api_key=api_key, api_base=api_base, large_model=large_model)
        parser.url_type = link_type
        return fetch_data(parser, link_type)
    except Exception as e:
        log.error(f"Error in fetch_ggzy_qz: {e},{traceback.format_exc()}")
        return "text", None


def fetch_ggzyjy_jinhua(url, link_type, keyword, max_day, api_key, api_base, large_model):
    from crawler.adapted_parsing_methods.jinhua import JinhuaParser
    try:
        parser = JinhuaParser(url=url, headers={"User-Agent": "Mozilla/5.0"}, keyword=keyword, max_day=max_day,
                              api_key=api_key, api_base=api_base, large_model=large_model)
        parser.url_type = link_type
        return fetch_data(parser, link_type)
    except Exception as e:
        log.error(f"Error in fetch_ggzyjy_jinhua: {e},{traceback.format_exc()}")
        return "text", None


def fetch_ggzy_hangzhou(url, link_type, keyword, max_day, api_key, api_base, large_model):
    from crawler.adapted_parsing_methods.hangzhou import HangzhouParser
    try:
        parser = HangzhouParser(url=url, headers={"User-Agent": "Mozilla/5.0"}, keyword=keyword, max_day=max_day,
                                api_key=api_key, api_base=api_base, large_model=large_model)
        parser.url_type = link_type
        return fetch_data(parser, link_type)
    except Exception as e:
        log.error(f"Error in fetch_ggzy_hangzhou: {e}，{traceback.format_exc()}")
        return "text", None


def fetch_ggzyjyeweb_wenzhou(url, link_type, keyword, max_day, api_key, api_base, large_model):
    from crawler.adapted_parsing_methods.wenzhou import WenzhouParser
    try:
        parser = WenzhouParser(url=url, headers={"User-Agent": "Mozilla/5.0"}, keyword=keyword, max_day=max_day,
                               api_key=api_key, api_base=api_base, large_model=large_model)
        parser.url_type = link_type
        return fetch_data(parser, link_type)
    except Exception as e:
        log.error(f"Error in fetch_ggzyjyeweb_wenzhou: {e},{traceback.format_exc()}")
        return "text", None


def fetch_jxszwsjb_jiaxing(url, link_type, keyword, max_day, api_key, api_base, large_model):
    from crawler.adapted_parsing_methods.jiaxing import JiaxingParser
    try:
        parser = JiaxingParser(url=url, headers={"User-Agent": "Mozilla/5.0"}, keyword=keyword, max_day=max_day,
                               api_key=api_key, api_base=api_base, large_model=large_model)
        parser.url_type = link_type
        return fetch_data(parser, link_type)
    except Exception as e:
        log.error(f"Error in fetch_jxszwsjb_jiaxing: {e},{traceback.format_exc()}")
        return "text", None


def fetch_ggzyjy_huzhou(url, link_type, keyword, max_day, api_key, api_base, large_model):
    from crawler.adapted_parsing_methods.huzhou import HuzhouParser
    try:
        parser = HuzhouParser(url=url, headers={"User-Agent": "Mozilla/5.0"}, keyword=keyword, max_day=max_day,
                              api_key=api_key, api_base=api_base, large_model=large_model)
        parser.url_type = link_type
        return fetch_data(parser, link_type)
    except Exception as e:
        log.error(f"Error in fetch_ggzyjy_huzhou: {e}，{traceback.format_exc()}")
        return "text", None


def fetch_zsztb_zhoushan(url, link_type, keyword, max_day, api_key, api_base, large_model):
     from crawler.adapted_parsing_methods.zhoushan import ZhoushanParser
     try:
         parser = ZhoushanParser(url=url, headers={"User-Agent": "Mozilla/5.0"}, keyword=keyword, max_day=max_day,
                                 api_key=api_key, api_base=api_base, large_model=large_model)
         parser.url_type = link_type
         return fetch_data(parser, link_type)
     except Exception as e:
         log.error(f"Error in fetch_zsztb_zhoushan: {e},{traceback.format_exc()}")
         return "text", None


def fetch_tzztb_zjtz(url, link_type, keyword, max_day, api_key, api_base, large_model):
    from crawler.adapted_parsing_methods.taizhou import TaizhouParser
    try:
        parser = TaizhouParser(url=url, headers={"User-Agent": "Mozilla/5.0"}, keyword=keyword, max_day=max_day,
                               api_key=api_key, api_base=api_base, large_model=large_model)
        parser.url_type = link_type
        return fetch_data(parser, link_type)
    except Exception as e:
        log.error(f"Error in fetch_tzztb_zjtz: {e},{traceback.format_exc()}")
        return "text", None


def fetch_lssggzy_lishui(url, link_type, keyword, max_day, api_key, api_base, large_model):
     from crawler.adapted_parsing_methods.lishui import LishuiParser
     try:
         parser = LishuiParser(url=url, headers={"User-Agent": "Mozilla/5.0"}, keyword=keyword, max_day=max_day,
                               api_key=api_key, api_base=api_base, large_model=large_model)
         parser.url_type = link_type
         return fetch_data(parser, link_type)
     except Exception as e:
         log.error(f"Error in fetch_lssggzy_lishui: {e},{traceback.format_exc()}")
         return "text", None




class AbstractWebCrawler(ABC):
    def __init__(self, url, headers=None, params=None, proxies=None, data=None, method="GET", max_page=None,
                 keyword=None,max_day=30):
        """
        初始化网页查询工具的基础属性。
        :param url: 查询目标 URL
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
        # 数据类型
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
        self.max_page = max_page or 1
        self.keyword = keyword or ""
        self.max_day = max_day or 30


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
        运行整个查询工具过程：获取内容 -> 解析。
        """
        if not self.url:
            raise ValueError("URL不能为空。")
        self.fetch()
        self.parse()
