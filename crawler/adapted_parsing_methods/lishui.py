import re

from bs4 import BeautifulSoup
from html2text import html2text

from .qz import QzParser


class LishuiParser(QzParser):
    pass
    def parse_html(self):
        target_divs = self.html_content.find_all('script', type='text/xml')
        data_list = []
        for target_div in target_divs:
            target_div = target_div.string.strip()
            target_div = BeautifulSoup(target_div, 'xml')
            records = target_div.find_all('record')

            for record in records:
                record_content = record.string.strip()
                record_soup = BeautifulSoup(record_content, 'html.parser')

                # 提取每个记录的链接和标题
                link_tag = record_soup.find('li')
                link =  self.scheme + "://" + self.domain + link_tag.get('data-colurl')
                data = (1, link, "table")
                if data not in data_list:
                    data_list.append(data)
        self.response_type = "url_list"
        self.response = data_list


    def get_file_info(self):
        file_info = self.html_content.find_all("a",href=True)

        res = []
        for info in file_info:
            if "cmd=download" in info.get("href"):
                info["href"] = re.sub(r'(\d{1,3}\.){3}\d{1,3}',"dzjy.lssggzy.lishui.gov.cn",info["href"])
                res.append(info)
        return res

    def get_content(self):
        content = self.html_content.find("div", class_="article-conter")
        if not content:
            content = "test"
        content = html2text(str(content))
        return content


