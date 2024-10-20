
from urllib.parse import urlparse, parse_qs


from core.history_manager import HistoryManager
from log.logger import Logger
from .qz import QzParser

log = Logger().get_logger()

history_manager = HistoryManager()


def get_ground_table_url(url, html):
    domain = urlparse(url).netloc
    scheme = urlparse(url).scheme
    res = set()
    html_soup = html.select("div.list_tt")
    for item in html_soup:
        item_url = item.find('a')['href']
        if item_url.startswith('http'):
            res.add(item_url)
        else:
            res.add(scheme + "://" + domain + item_url)
    return [(1, item, "table") for item in res]
    # return [(1, res[1], "table")]


class JinhuaParser(QzParser):
    """
    This class is used to parse the html content of Jinhua website.
    url: http://ggzyjy.jinhua.gov.cn
    """

    PAGE_ID = "7642408"

    def parse_html(self):
        ground_table_urls = get_ground_table_url(self.url, self.html_content)
        self.response_type = 'url_list'
        self.response = ground_table_urls

