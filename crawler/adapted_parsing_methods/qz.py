import requests
from bs4 import BeautifulSoup

from .manager import AbstractWebCrawler
from ui.main_window import WebCrawlerApp


class QzParser(AbstractWebCrawler):
    def fetch(self):
        headers = self.headers

        response = self.session.get(self.url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.html_content = soup

    def parse(self):
        if self.html_content is None:
            return None
        elif self.html_content is not None:
            # TODO: 解析 HTML 内容并提取数据，返回字典列表，进入第三层爬虫
            script_tag = self.html_content.find('script', type='text/xml')
            if script_tag:
                xml_content = script_tag.string
                # 将内容解析为 BeautifulSoup 对象
                xml_soup = BeautifulSoup(xml_content, 'xml')

                # 提取 <record> 数据
                records = xml_soup.find_all('record')
                data_list = []

                for record in records:
                    # 提取 CDATA 内容并解析成 HTML
                    record_content = record.string.strip()
                    record_soup = BeautifulSoup(record_content, 'html.parser')

                    # 提取每个记录的链接和标题
                    link = record_soup.find('a')['href']
                    title = record_soup.find('a').text
                    date = record_soup.find('span', class_='ewb-col-date').text

                    # 将数据存入列表
                    data_list.append({
                        'link': link,
                        'title': title,
                        'date': date
                    })

                # 打印提取的数据
                for data in data_list:
                    print(data)
            else:
                print("没有找到包含数据的 <script> 标签。")
