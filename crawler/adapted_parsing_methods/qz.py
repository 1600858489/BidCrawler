import datetime
import os
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup

from core.history_manager import HistoryManager
from .manager import AbstractWebCrawler
from log.logger import Logger

log = Logger().get_logger()

history_manager = HistoryManager()

class QzParser(AbstractWebCrawler):
    def fetch(self):
        log.info(f"Fetching {self.url}")
        headers = self.headers

        try:
            response = self.session.get(self.url, headers=headers)
            if response.status_code == 200:
                log.info(f"Fetch successful for {self.url}")
                log.info(f"response content: {response.status_code}")
                self.html_content = BeautifulSoup(response.content, 'html.parser')
            else:
                log.error(f"Fetch failed for {self.url}")
                log.error(f"response status code: {response.status_code}")
                log.error(f"response content: {response.content}")
                self.html_content = None
        except Exception as e:
            log.error(f"Fetch failed for {self.url}")
            log.error(f"Error: {e}")

        try:
            log.info(f"self.session history: {self.session.history[-1].url}")
        except:
            pass





    def parse(self):

        if self.html_content is None:
            return None
        elif self.html_content is not None:
            domain = urlparse(self.url).netloc
            scheme = urlparse(self.url).scheme
            if self.url_type == "html":
                target_div = self.html_content.select_one("#tab1 > div:nth-child(1) > ul")
                res = []

                for tag in target_div.select('li'):
                    link = tag.get('href')
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
                            link = scheme + "://" + domain + link
                            if not history_manager.is_in_history(link):
                                data_list.append((1, link, "detail_page"))
                            else:
                                log.info(f"link is in history, skip {link}")

                        except Exception as e:
                            log.error(f"analysis record data failed: {e}")
                            continue

                    now_page_num = parse_qs(urlparse(self.url).query).get('pageNum', [False])[0]

                    if not now_page_num:
                        if self.max_page >= 2:
                            next_page_num = 2
                            next_url = self.url + "&uid=7872499&pageNum=" + str(next_page_num)
                            data_list.append((1, next_url, "table"))
                        else:
                            log.info(f"crawled all pages, stop")
                    else:
                        if int(now_page_num) < self.max_page:
                            next_page_num = int(now_page_num) + 1
                            next_url = self.url.replace("pageNum=" + str(now_page_num), "pageNum=" + str(next_page_num))
                            data_list.append((1, next_url, "table"))

                    if data_list:
                        self.response_type = "url_list"
                        self.response = data_list

            elif self.url_type == "detail_page":
                title = self.html_content.find('title').text.strip()
                content = self.html_content.find('div', class_='ewb-content').text.strip().split('。')[0] + ("。"

                                                                                                            "")
                file_info = self.html_content.select('#fileDownd a')
                is_file = True if file_info else False
                res = []
                one_file_path = self.file_path + "/" + domain + "/" + title
                if not os.path.exists(one_file_path):
                    os.makedirs(one_file_path)

                while file_info:
                    file = file_info.pop(0)
                    file_url = file['href']
                    file_name = file.text.strip()
                    file_path = one_file_path + "/" + file_name
                    log.info(f"downloading file: {file_name}")
                    if self.file_download(file_url, file_path):
                        continue

                with open(one_file_path + "/" + title + ".txt", 'w', encoding='utf-8') as f:
                    f.write(content)
                self.response_type = "text"
                self.response = one_file_path

                history_manager.add_to_history(
                    url=self.url,
                    has_attachment=is_file,
                    attachment_path=one_file_path,
                    platform="衢州市政府",
                    timestamp=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    description="test"
                )

    def file_download(self, file_url, file_path):
        log.info(f"downloading file: {file_url}")
        headers = self.headers
        response = self.session.get(file_url, headers=headers, stream=True)
        if response.status_code != 200:
            log.error(f"download file failed: {file_url}")
            return False
        log.info(f"download file successful: {file_url}")
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        return True
