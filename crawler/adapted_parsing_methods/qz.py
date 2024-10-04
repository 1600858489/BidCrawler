import os
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .manager import AbstractWebCrawler


class QzParser(AbstractWebCrawler):
    def fetch(self):
        headers = self.headers

        response = self.session.get(self.url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.html_content = soup

    def parse(self):
        print(self.response_type)
        if self.html_content is None:
            return None
        elif self.html_content is not None:
            if self.url_type == "html":
                target_div = self.html_content.select_one("#tab1 > div:nth-child(1) > ul")
                res = []

                for tag in target_div.select('li'):
                    link = tag.get('href')
                    domain = urlparse(self.url).netloc
                    scheme = urlparse(self.url).scheme
                    res.append((1, scheme + "://" + domain + link, "table"))

                self.response_type = "url_list"
                self.response = [res[0]]


            elif self.url_type == "table":
                # TODO: 解析 HTML 内容并提取数据，返回字典列表，进入第三层爬虫
                script_tag = self.html_content.find('script', type='text/xml')
                if script_tag:
                    xml_content = script_tag.string
                    # 将内容解析为 BeautifulSoup 对象
                    try:
                        xml_soup = BeautifulSoup(xml_content, 'xml')
                    except Exception as e:
                        print(f"解析 XML 内容失败：{e}")
                        return None

                    # 提取 <record> 数据
                    records = xml_soup.find_all('record')
                    data_list = []

                    for record in records:
                        # 提取 CDATA 内容并解析成 HTML
                        record_content = record.string.strip()
                        record_soup = BeautifulSoup(record_content, 'html.parser')

                        # 提取每个记录的链接和标题
                        link = record_soup.find('a')['href']

                        # 将数据存入列表
                        try:
                            domain = urlparse(self.url).netloc
                            scheme = urlparse(self.url).scheme
                            data_list.append((1, scheme + "://" + domain + link, "detail_page"))

                        except Exception as e:
                            print(f"解析记录数据失败：{e}")
                            continue
                    next_page_tag = self.html_content.find('a', title='下页')
                    if next_page_tag:
                        next_page_url = next_page_tag['href']
                        data_list.append((1, next_page_url, "control"))

                    if data_list:
                        self.response_type = "url_list"
                        self.response = data_list

            elif self.url_type == "detail_page":
                title = self.html_content.find('title').text.strip()
                content = self.html_content.find('div', class_='ewb-content').text.strip().split('。')[0] + ("。"

                                                                                                            "")
                file_info = self.html_content.select('#fileDownd a')
                res = []
                one_file_path = self.file_path + "/" + title
                if not os.path.exists(one_file_path):
                    os.makedirs(one_file_path)

                while file_info:
                    file = file_info.pop(0)
                    file_url = file['href']
                    file_name = file.text.strip()
                    file_path = one_file_path + "/" + file_name
                    if self.file_download(file_url, file_path):
                        continue

                with open(one_file_path + "/" + title + ".txt", 'w', encoding='utf-8') as f:
                    f.write(content)
                self.response_type = "text"
                self.response = one_file_path

    def file_download(self, file_url, file_path):
        headers = self.headers
        response = self.session.get(file_url, headers=headers, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True
