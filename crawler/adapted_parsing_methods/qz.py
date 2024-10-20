import datetime
import os
import re
from urllib.parse import urlparse, parse_qs

import pandas as pd
from bs4 import BeautifulSoup
import html2text
from tqdm import tqdm

from core.history_manager import HistoryManager
from log.logger import Logger
from .manager import AbstractWebCrawler
from config import *

log = Logger().get_logger()

history_manager = HistoryManager()

class QzParser(AbstractWebCrawler):
    """
    This class is used to parse the Qz.com website.
    url: http://ggzy.qz.gov.cn/
    """
    PAGE_ID = "7872499"
    def __init__(self, url, headers=None, params=None, proxies=None, data=None, method="GET", max_page=None,
                 keyword=None,max_day=None):
        super().__init__(url, headers, params, proxies, data, method, max_page, keyword,max_day)
        self.scheme = None
        self.domain = None
        self.target_name = None


    def fetch(self):
        log.info(f"Fetching {self.url}")
        headers = self.headers

        try:
            response = self.session.get(self.url, headers=headers,timeout=60)
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

    def set_next_page(self):
        now_page_num = parse_qs(urlparse(self.url).query).get('pageNum', [False])[0]

        # 计算下一页的 URL
        if not now_page_num:
            if self.max_page >= 2:
                next_url = f"{self.url}&uid={self.PAGE_ID}&pageNum=2"
                return next_url
            else:
                log.info("已经查询所有页面，停止")
        else:
            now_page_num = int(now_page_num)
            if now_page_num < self.max_page:
                next_url = self.url.replace(f"pageNum={now_page_num}", f"pageNum={now_page_num + 1}")
                return next_url

    def parse_html(self):
        target_div = self.html_content.select_one("#tab1 > div:nth-child(1) > ul")
        res = []

        for tag in target_div.select('li'):
            link = tag.get('href')
            res.append((1, self.scheme + "://" + self.domain + link, "table"))
        self.response_type = "url_list"
        self.response = res

    def not_in_time(self, link):
        time_tag = re.search(r'/(\d{4})/(\d{1,2})/(\d{1,2})/', link)
        time_str = "-".join(time_tag.groups())
        time_obj = datetime.datetime.strptime(time_str, '%Y-%m-%d')
        return self.max_day and (datetime.datetime.now() - time_obj).days > self.max_day


    def parse_table(self):
        script_tag = self.html_content.find('script', type='text/xml')
        if not script_tag:
            log.error("没有找到合适的 script 标签")
            return None

        xml_content = script_tag.string

        # 将内容解析为 BeautifulSoup 对象
        try:
            xml_soup = BeautifulSoup(xml_content, 'xml')
        except Exception as e:
            log.error(f"解析 XML 内容失败：{e}")
            return None

        # 提取 <record> 数据
        records = xml_soup.find_all('record')
        data_list = []

        for record in records:
            # 提取 CDATA 内容并解析成 HTML
            record_content = record.string.strip()
            record_soup = BeautifulSoup(record_content, 'html.parser')

            # 提取每个记录的链接和标题
            link_tag = record_soup.find('a')
            if link_tag:
                link = link_tag['href']
                title = link_tag['title']
                link = self.scheme + "://" + self.domain + link
                if self.not_in_time(link):
                    continue
                if self.keyword and self.keyword not in title:
                    continue
                if  history_manager.is_in_history(link):
                    continue
                data_list.append((1, link, "detail_page"))
            else:
                log.warning("记录中没有链接")

        next_page_url = self.set_next_page()
        if next_page_url:
            data_list.append((1, next_page_url, "table"))


        if data_list:
            self.response_type = "url_list"
            self.response = data_list


    def set_file_path(self):
        level3_path =  self.html_content.select_one("span#col2_name").text.strip()
        level4_path =  self.html_content.select_one("span#col1_name").text.strip()
        return f"/{level3_path}/{level4_path}"

    def get_content(self):
        content_div = self.html_content.select_one('div.ewb-detail-content.ewb-mt20 > div')
        if not content_div:
            content_div = ""

        return html2text.html2text(str(content_div))


    def save_announcement(self,file_path):
        table =  self.html_content.find('table', style="font-size:18px; font-family:'宋体'; line-height:2")

# 存储提取的数据
        data = []
        # 遍历表格的行
        for row in table.find_all('tr'):  # 从第三行开始提取数据（跳过表头）
            cols = row.find_all('td')
            if len(cols) == 6:  # 确保行中有足够的列
                # 提取每一列的数据并去掉前后空白
                data.append([col.get_text(strip=True) for col in cols])

        data = data[1:]  # 去掉表头
        # 将数据转换为 DataFrame，并设置列名
        columns = ['标段（包）编号', '标段（包）名称', '中标单位', '项目经理', '中标价格', '工期（天）']
        df = pd.DataFrame(data, columns=columns)
        output_file = file_path + "/中标结果公告.csv"
        if os.path.exists(output_file):
            df.to_csv(output_file, mode='a', index=False, header=False, encoding='utf-8-sig')  # 追加数据，不写表头
        else:
            df.to_csv(output_file, index=False, encoding='utf-8-sig')  # 如果文件不存在，写入表头
        return True


    def get_file_info(self):
        return self.html_content.select('#fileDownd a')


    def parse_detail_page(self):

        title = self.html_content.find('title').text.strip()
        content = self.get_content()
        file_info = self.get_file_info()
        is_file = True if file_info else False
        one_file_path = self.file_path + "/" + self.domain  + self.set_file_path() + "/" + title
        if not os.path.exists(one_file_path):
            os.makedirs(one_file_path)

        if "中标结果公告" in  one_file_path:
            announcement_path = one_file_path.replace("/" + title, "")
            self.save_announcement(announcement_path)

        while file_info:
            file = file_info.pop(0)
            print(file)
            file_url = file['href']
            file_name = file.text.strip()
            num = 0
            while os.path.exists(one_file_path + "/" + file_name):
                file_name = file_name.split('.')[0] + f"({num})" + "." + file_name.split('.')[1]
                num += 1
            file_path = one_file_path + "/" + file_name
            log.info(f"downloading file: {file_name}")
            if self.file_download(file_url, file_path):
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
            timestamp=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            description="test"
        )


    def parse(self):

        if self.html_content is None:
            self.response_type = "url_list"
            self.response = []
        elif self.html_content is not None:
            self.domain = urlparse(self.url).netloc
            self.scheme = urlparse(self.url).scheme
            if self.url_type == "html":
                self.parse_html()

            elif self.url_type == "table":
                self.parse_table()

            elif self.url_type == "detail_page":
                self.parse_detail_page()

    def file_download(self, file_url, file_path):
        log.info(f"downloading file: {file_url}")
        headers = self.headers
        max_retries = 3  # 最大重试次数
        retries = 0  # 当前重试计数

        while retries < max_retries:
            try:
                response = self.session.get(file_url, headers=headers, stream=True, timeout=60)
                if response.status_code == 200:
                    log.info(f"download file successful: {file_url}")

                    total_size = int(response.headers.get('content-length', 0))  # 获取文件总大小
                    with open(file_path, 'wb') as f:
                        # 使用tqdm显示进度条
                        with tqdm(total=total_size, unit='B', unit_scale=True, desc=file_url.split('/')[-1]) as pbar:
                            for chunk in response.iter_content(chunk_size=1024):
                                if chunk:
                                    f.write(chunk)
                                    pbar.update(len(chunk))  # 更新进度条

                    return True
                else:
                    log.error(f"download file failed with status code {response.status_code}: {file_url}")
            except Exception as e:
                log.error(f"exception occurred while downloading file: {e}")

            retries += 1
            log.info(f"retrying... ({retries}/{max_retries})")

        log.error(f"failed to download file after {max_retries} attempts: {file_url}")
        return False

