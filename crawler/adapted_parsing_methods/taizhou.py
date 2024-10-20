import os
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from html2text import html2text
from win32ctypes.pywin32.pywintypes import datetime

from core.history_manager import HistoryManager
from log.logger import Logger
from .qz import QzParser


history_manager = HistoryManager()
log = Logger().get_logger()


class TaizhouParser(QzParser):
    """
    This class inherits from QzParser and implements the specific parsing methods for taizhou.com.
    url: http://ggzy.tzztb.zjtz.gov.cn
    """

    MAIN_TABLE_PAGE_URL = "https://ggzy.tzztb.zjtz.gov.cn/jyxx/002001/trade_infor.html"

    def parse_html(self):
        parsed_url = urlparse(self.url)
        if parsed_url.path == "/":
            url = self.MAIN_TABLE_PAGE_URL
            res = [(1, url, "html")]
            self.response_type = "url_list"
            self.response = res
            return

        targets_div = self.html_content.find("div",id='isopen_002001')
        res = []
        if not targets_div:
            return
        for target_li in targets_div.find_all("li"):
            url = self.scheme + "://" + self.domain + target_li.get('data-categoryurl')
            ans = (1, url,"table")
            if ans in res:
                continue
            res.append(ans)

        self.response_type = "url_list"
        self.response = res


    def parse_table(self):
        targets_a = self.html_content.find_all("a", class_='public-list-item')
        if not targets_a:
            return
        res = []
        for target_a in targets_a:
            url = self.scheme + "://" + self.domain + target_a.get('href')
            title = target_a.get('title')
            date = target_a.find("span", class_='date').text.strip()

            time_obj = datetime.strptime(date, '%Y-%m-%d')

            if self.max_day and (datetime.now() - time_obj).days > self.max_day:
                continue
            if history_manager.is_in_history(url):
                continue
            if self.keyword and self.keyword not in title:
                continue
            ans = (1, url, "detail_page")
            if ans in res:
                continue
            res.append(ans)

        self.response_type = "url_list"
        self.response = res


    def get_content(self):
        content = self.html_content.find("div", class_='container')
        if not content:
            content = "#test"
        content = html2text(str(content))
        return content

    def get_file_info(self):
        file_info = self.html_content.select("#attachlist .file-item")
        if not file_info:
            return []
        res = []
        for file in file_info:
            file_url = self.scheme + "://" + self.domain + file.find('a')['onclick'].split("'")[1]
            file_name = file.select_one('span[title]').get('title')
            print(file_url, file_name)
            res.append({
                "file_name": file_name,
                "href": file_url
            })
        return res

    def set_file_path(self):
        level3_path =  "工程建设"
        level4_path =  self.html_content.select_one("span#viewGuid").text.strip()
        return f"/{level3_path}/{level4_path}"


    def parse_detail_page(self):

        title = self.html_content.select_one("p.main-title").text.strip()
        content = self.get_content()
        file_info = self.get_file_info()
        is_file = True if file_info else False
        one_file_path = self.file_path + "/" + self.domain  + self.set_file_path() + "/" + title
        if not os.path.exists(one_file_path):
            os.makedirs(one_file_path)

        # if "中标结果公告" in  one_file_path:
        #     announcement_path = one_file_path.replace("/" + title, "")
        #     self.save_announcement(announcement_path)

        while file_info:
            try:
                file = file_info.pop(0)
                file_url = file['href']
                file_name = file['file_name']
                num = 0
                while os.path.exists(one_file_path + "/" + file_name):
                    file_name = file_name.split('.')[0] + f"({num})" + "." + file_name.split('.')[1]
                    num += 1
                file_path = one_file_path + "/" + file_name
                log.info(f"downloading file: {file_name}")
                if self.file_download(file_url, file_path):
                    continue
            except Exception as e:
                log.error(f"download file error: {e}")
                continue

        with open(one_file_path + "/" + title + ".md", 'w', encoding='utf-8') as f:
            f.write(content)
        self.response_type = "text"
        self.response = one_file_path

        history_manager.add_to_history(
            url=self.url,
            has_attachment=is_file,
            attachment_path=one_file_path,
            platform=self.domain,
            timestamp=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            description="test"
        )
