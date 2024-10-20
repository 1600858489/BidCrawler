import re
from urllib.parse import urlparse, parse_qs

from html2text import html2text

from core.history_manager import HistoryManager
from log.logger import Logger
from .qz import QzParser

log = Logger().get_logger()
history_manager = HistoryManager()

class ZhoushanParser(QzParser):
    """
    This class is used to parse the Zhoushan website.
    url: http://zsztb.zhoushan.gov.cn/
    """
    MAIN_TABLE_PAGE_URL = "http://ggzy.tzztb.zjtz.gov.cn/jyxx/002001/trade_infor.html"
    def parse_html(self):
        parsed_url = urlparse(self.url+"/")
        if parsed_url.path == "/":
            url = self.MAIN_TABLE_PAGE_URL
            res = [(1, url, "html")]
            self.response_type = "url_list"
            self.response = res
            return
        targets_div = self.html_content.select("ul.trade-top-list li.trade-top-item")
        res = []
        if not targets_div:
            return
        for target in targets_div:
            url = self.scheme + "://" + self.domain + target.select_one("a")["href"]
            ans = (1, url, "table")
            if ans not in res:
                res.append(ans)
        self.response_type = "url_list"
        self.response = res


    def parse_table(self):
        script_tag = self.html_content.find_all("script",language="javascript")[2]
        script_content = script_tag.string
        urls = re.findall(r"urls\[iii\]='(.*?)';", script_content)
        title = re.findall(r"headers\[iii\]='(.*?)';", script_content)
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

    def get_content(self):
        context = self.html_content.find("div", {"class": "container"})
        if not context:
            context= "# 无数据"
        md = html2text(str(context))
        return md

    def get_file_info(self):
        file_info = []
        file_links = self.html_content.select("a")
        for file_link in file_links:
            if "downloadztbattach" in file_link.get("href"):
                file_info.append(file_link.get("href"))
        return file_info
