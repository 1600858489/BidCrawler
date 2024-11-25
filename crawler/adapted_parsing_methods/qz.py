import datetime
import re
from urllib.parse import urlparse, parse_qs

import html2text
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

from config import *
from core.bot.chatgpt.chatgpt import OpenAIChatClient
from core.file_read.pdf import read_pdf
from core.file_read.word import read_and_convert_doc
from core.history_manager import HistoryManager
from log.logger import Logger
from .manager import AbstractWebCrawler

log = Logger().get_logger()

history_manager = HistoryManager()


class QzParser(AbstractWebCrawler):
    """
    This class is used to parse the Qz.com website.
    url: http://ggzy.qz.gov.cn/
    """

    def __init__(self, url, headers=None, params=None, proxies=None, data=None, method="GET", max_page=None,
                 keyword=None, max_day=None, api_key=None, api_base=None, large_model=False):
        super().__init__(url, headers, params, proxies, data, method, max_page, keyword,max_day)
        self.scheme = None
        self.domain = None
        self.target_name = None
        self.api_key = api_key
        self.api_base = api_base
        self.large_model = large_model

        print(self.large_model)


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
                self.error_msg = f"Fetch failed for {self.url}, response status code: {response.status_code}, response content: {response.content}"
        except Exception as e:
            log.error(f"Fetch failed for {self.url}")
            log.error(f"Error: {e}")
            self.html_content = None
            print()
            self.error_msg = f"Fetch failed for {self.url}, error: {e}"

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
            self.response_type = "error"
            self.error_msg = "没有找到合适的详情信息"
            return

        xml_content = script_tag.string

        # 将内容解析为 BeautifulSoup 对象
        try:
            xml_soup = BeautifulSoup(xml_content, 'xml')
        except Exception as e:
            log.error(f"解析 XML 内容失败：{e}")
            self.response_type = "error"
            self.error_msg = f"解析内容失败，错误信息：{e}"
            return None

        # 提取 <record> 数据
        records = xml_soup.find_all('record')
        data_list = []

        for record in records:
            # 提取 CDATA 内容并解析成 HTML
            record_content = record.string.strip()
            record_soup = BeautifulSoup(record_content, 'html.parser')

            # 提取每个记录的链接和标题
            # link_tag = record_soup.find('as')
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



        self.response_type = "url_list"
        self.response = data_list


    def set_file_path(self):
        level3_path =  self.html_content.select_one("span#col2_name").text.strip()
        level4_path =  self.html_content.select_one("span#col1_name").text.strip()
        return f"/{level3_path}/{level4_path}"

    def get_content(self):
        content_div = self.html_content.select_one('div.ewb-detail-content.ewb-mt20 > div')
        if not content_div:
            content_div = "no text data"

        return html2text.html2text(str(content_div))

    def save_announcement(self,domain: str, content: str, images: list, template=None) -> bool:
        if not self.large_model:
            return False
        log.info(f"save announcement: {len(content)}")
        if images:
            content += "\n\n" + "## 请借助该文本与图片提取出我需要的信息"

        json_data = OpenAIChatClient(api_key=self.api_key, api_base=self.api_base).get_response(content, images,
                                                                                                template)
        if not json_data:
            log.error("OpenAI Chat Client 调用失败")
            return False
        columns = ['域','标段（包）编号', '标段（包）名称', '中标单位', '项目经理', '中标价格', '工期（天）', '其他信息']
        df = pd.DataFrame([[
            domain,
            json_data.get("section_id"),
            json_data.get("section_name"),
            json_data.get("winning_company"),
            json_data.get("project_manager"),
            json_data.get("winning_price"),
            json_data.get("duration_days"),
            json_data.get("other")
        ]], columns=columns)
        log.info(f"save announcement to csv: {ANNOUNCEMENT_PATH}")
        if not os.path.exists(ANNOUNCEMENT_PATH):
            df.to_csv(ANNOUNCEMENT_PATH, mode='w', header=True, index=False)
        else:
            df.to_csv(ANNOUNCEMENT_PATH, mode='a', header=False, index=False)
        return True

    def save_pre_announcement(self, domain: str,content: str, images: list, template=None) -> bool:
        if not self.large_model:
            return False
        log.info(f"save pre announcement")

        if images:
            content += "\n\n" + "## 请借助该文本与图片提取出我需要的信息"

        json_data = OpenAIChatClient(api_key=self.api_key, api_base=self.api_base).get_response(content, images,
                                                                                                template)
        if not json_data:
            log.error("OpenAI Chat Client 调用失败")

            return False
        columns = ['域','标段（包）编号', '标段（包）名称', '预中标单位', '项目经理', '预中标价格', '工期（天）', '评分']

        rows = []
        for i in range(len(json_data.get("pre_winning_company"))):
            row = {
                "域": domain,
                "标段（包）编号": json_data.get("section_id"),
                "标段（包）名称": json_data.get("section_name"),
                "预中标单位": json_data.get("pre_winning_company")[i],
                "项目经理": json_data.get("project_manager")[i],
                "预中标价格": json_data.get("pre_winning_price")[i],
                "工期（天）": json_data.get("duration_days")[i],
                "评分": json_data.get("score")[i]
            }
            rows.append(row)
        df = pd.DataFrame(rows, columns=columns)
        log.info(f"save pre announcement to csv: {PRE_ANNOUNCEMENT_PATH}")
        if not os.path.exists(PRE_ANNOUNCEMENT_PATH):
            df.to_csv(PRE_ANNOUNCEMENT_PATH, mode='w', header=True, index=False)
        else:
            df.to_csv(PRE_ANNOUNCEMENT_PATH, mode='a', header=False, index=False)
        return True


    def get_file_info(self):
        return self.html_content.select('#fileDownd a')

    def get_file_content(self, file_paths):
        texts = ""
        base_images = []
        for file_path in file_paths:

            if "pdf" in file_path:
                text, base_image = read_pdf(file_path)
                if len(base_image) > 0: base_images.append(base_image)
                if len(text) > len(texts): texts = text
            elif "docx" or "doc" in file_path:
                text = read_and_convert_doc(file_path)
                if len(text) > len(texts): texts = text

        return texts, base_images

    def get_title(self):
        return self.html_content.find('title').text.strip().replace("/", "")

    def is_process_announcement(self, content: str) -> bool:
        keyword = ["中标结果公告", "中标公告"]

        return any(key in content for key in keyword)

    def is_process_pre_announcement(self, content: str) -> bool:
        keyword = ["预中标公告"]
        return any(key in content for key in keyword)

    def get_file_description(self, file_info):
        file_url = file_info['href']
        file_name = file_info.text.strip()

        return file_url, file_name


    def save_content2md(self, content: str, file_path: str, title: str):
        with open(file_path + "/" + title + ".md", 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write("=" * len(title) + "\n\n")
            f.write(content)
        return True

    def download_file(self, file_info, one_file_path):

        file_save_path = []
        while file_info:
            file = file_info.pop(0)
            file_url, file_name = self.get_file_description(file)
            num = 0
            while os.path.exists(one_file_path + "/" + file_name):
                file_name = file_name.split('.')[0] + f"({num})" + "." + file_name.split('.')[1]
                num += 1
            file_path = one_file_path + "/" + file_name
            log.info(f"downloading file: {file_name}")
            log.info(f"downloading file: {file_url}")
            if self.file_download(file_url, file_path):
                file_save_path.append(file_path)
                continue
        return file_save_path

    def set_one_file_path(self,title):
        return self.file_path + "/" + PLATFORM_HASH.get(self.domain, self.domain) + self.set_file_path() + "/" + title


    def save_history(self,is_file,one_file_path):
        history_manager.add_to_history(
            url=self.url,
            has_attachment=is_file,
            attachment_path=one_file_path,
            platform=self.domain,
            timestamp=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            description="test"
        )


    def parse_detail_page(self):

        title = self.get_title()
        content = self.get_content()
        file_info = self.get_file_info()
        is_file = True if file_info else False
        one_file_path = self.set_one_file_path(title)


        if not os.path.exists(one_file_path):
            os.makedirs(one_file_path)

        file_save_path = self.download_file(file_info, one_file_path)



        if self.large_model and file_save_path:

            if self.is_process_announcement(one_file_path):
                text, image = self.get_file_content(file_save_path)
                if len(image) > 200:
                    i
                self.save_announcement(PLATFORM_HASH.get(self.domain, self.domain),content, image)

            elif self.is_process_pre_announcement(one_file_path):
                text, image = self.get_file_content(file_save_path)
                self.save_pre_announcement(PLATFORM_HASH.get(self.domain, self.domain),content, image)


        self.save_content2md(content, one_file_path, title)
        self.response_type = "text"
        self.response = one_file_path
        self.save_history(is_file,one_file_path)




    def parse(self):

        if self.html_content is None:
            self.response_type = "error"
            self.response = self.error_msg
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

