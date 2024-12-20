import datetime
import random
import time
import traceback

from html2text import html2text

from config import *
from core.history_manager import HistoryManager
from log.logger import Logger
from .qz import QzParser

log = Logger().get_logger()

history_manager = HistoryManager()



class HangzhouParser(QzParser):
    """
    This class is used to parse the Hangzhou website.
    url: https://ggzy.hzctc.hangzhou.gov.cn/
    """
    pass
    REQUESTS_JSON_URL = "https://ggzy.hzctc.hangzhou.gov.cn/SecondPage/GetNotice"
    REQUESTS_PAGE_URL = "https://ggzy.hzctc.hangzhou.gov.cn/AfficheShow/Home"


    PARAMS = {
        "area": "",
        "afficheType": "",
        "IsToday": "",
        "title": "",
        "proID": "",
        "number": "",
        "IsHistory": 0,
        "TenderNo": "",
        "_search": False,
        "nd": int(time.time()),
        "rows": 100,
        "page": 1,
        "sidx": "PublishStartTime",
        "sord": "desc"
    }
    AFFICHE_TYPE_MAP = {
    "bidding_plan": 519,  # 招标计划
    "core_information_announcement": 518,  # 核准信息公告
    "bidding_document_preannouncement": 505,  # 招标文件预公示
    "bidding_announcement": 22,  # 招标公告
    "query_document": 23,  # 答疑文件
    # "query_announcement": 465,  # 答疑公告
    "bid_opening_result_announcement": 486,  # 开标结果公示
    "pre_bid_winning_announcement": 25,  # 中标前公示
    "bid_winning_announcement": 28,  # 中标公告
    "project_contract": 506  # 项目合同
    }

    FILE_CODE_MAP = {
        'pdf':3,
    }
    """
    response_v ={
            "ID": "8894e9c2-7ff6-453e-bc8e-1110d697b1e0",
            "CodeName": "高新",
            "TenderName": "滨江区浦沿街道冠新佳苑三期物业管理服务项目",
            "TenderNo": "A3301080120190035001291",
            "PublishStartTime": "2024-10-10 16:25:00",
            "PublishEndTime": "2024-10-16 16:00:00",
            "ClickTimes": 0,
            "InArea": 73,
            "IsInner": 0
        },
        
    page_params = {
        "AfficheID": "8894e9c2-7ff6-453e-bc8e-1110d697b1e0", # response_v["ID"],
        "IsInner": 0, # response_v["IsInner"],
        "IsHistory": 0, # params["IsHistory"],
        "ModuleID": 34 # AFFICHE_TYPE_MAP[params["afficheType"]],
    }
    """

    # def __init__(self, url, headers=None, params=None, proxies=None, data=None, method="GET", max_page=None,
    #              keyword=None, max_day=None,):
    #     super().__init__(url, headers, params, proxies, data, method, max_page, keyword, max_day)

    def parse_html(self):
        """
        整体逻辑为：
        1. 发送请求，获取数据
        2. 解析数据，获取每条数据的ID

        """
        url_list = []
        for k,v in self.AFFICHE_TYPE_MAP.items():
            params = self.PARAMS.copy()
            params["page"] = 1
            params["rows"] = 5
            params["afficheType"] = str(v)
            params["nd"] = int(time.time())
            response = self.session.post(self.REQUESTS_JSON_URL, data=params, headers=self.headers)
            log.info("Requesting url: {}, params: {}".format(self.REQUESTS_JSON_URL, params))
            time.sleep(random.randint(1, 3))
            response_json = response.json()
            # print(response_json)
            if len(response_json.get("rows", [])) == 0:
                # print(response_json["rows"][1])
                log.info("No data found for params: {}".format(params))
                continue
            for item in response_json["rows"]:
                # print(item.get("ID", ""))
                try:
                    url = self.REQUESTS_PAGE_URL + "?AfficheID=" + (item.get("ID", "") or item.get("id", "")) + "&IsInner=" + str(item.get("IsInner",'0')) + "&IsHistory=" + str(params.get("IsHistory",'0')) + "&ModuleID=" + str(v)
                except KeyError as e:
                    print(e,traceback.format_exc(),item)
                    continue

                # print(url)
                # 条件判断
                # 1. 历史记录
                # 2. 关键字
                # 3. 时间限制
                # 4. 重复url
                if history_manager.is_in_history(url):
                    continue
                if self.keyword and self.keyword not in item["TenderName"]:
                    continue
                if self.max_day and (datetime.datetime.now() - datetime.datetime.strptime(item["PublishStartTime"], '%Y-%m-%d %H:%M:%S') ).days > self.max_day:
                    continue
                if url in url_list:
                    continue
                # 加入url_list
                url_list.append((1, url,"detail_page"))

                self.response_type = "url_list"
                self.response = url_list


    def get_content(self):
        """
        获取详情页内容
        :return:
        """
        context = self.html_content.find("div", class_="MainList")
        if not context:
            context = "# No data"
        md = html2text(str(context))
        return md


    def get_file_info(self):
        """
        获取文件信息
        :return:
        """
        # def set_file_url_name(filepath, showName):
        #     file_url = f"https://ggzy.hzctc.hangzhou.gov.cn/Uservice/DownLoadFile.aspx?dirtype=3&filepath={filepath}&showName={showName}"
        #     file_name = showName + "." + filepath.split(".")[-1]
        #     return file_url, file_name
        files_info = []
        links_info = self.html_content.find_all("a")
        while links_info:
            link = links_info.pop(0)
            if "DownLoad" in link.get("onclick", ""):
                link = link.get("onclick", None)
                if not link:
                    continue
                start = link.find("(") + 1
                end = link.find(")")
                file_info = link[start:end].replace("'", "").split(",")
                log.info(f"file_info: {file_info}")
                try:
                    file_hz = file_info[1].split(".")[-1]
                except IndexError:
                    file_hz = ""
                try:
                    file_url = self.get_download_file_url(file_info[0],file_info[1])
                    print(file_url)
                    files_info.append(
                        {
                            "name": file_info[0] + "." + file_hz,
                            "url": file_url,
                        }
                    )
                except Exception as e:
                    log.error(f"file_info is {file_info},file tag is {link}")
                    log.error(f"Get file url error: {e}, {traceback.format_exc()}")


        return files_info

    def get_download_file_url(self,file_name,file_id):

        data = {
            "FileDesc": file_name,
            "FilePath": file_id,
            "DirType": 3,
        }
        url = "https://ggzy.hzctc.hangzhou.gov.cn/AfficheShow/GetDownLoadUrl"
        try:
            file_url = self.session.post(url, data=data, headers=self.headers)
        except Exception as e:
            log.error(f"Get file url error: {e}, {traceback.format_exc()}")
            return ""
        if file_url.status_code == 200:
            file_url = file_url.text.strip()
            file_url = file_url.replace("+", "")
            return file_url
        log.error(f"Get file url error: {file_url.status_code}, {file_url.text}")
        return None

    def set_file_path(self):
        """
        设置文件路径
        :return:
        """
        target_div = self.html_content.find("span", {"class":"spanTitle"})

        if not target_div:
            return ""
        a_tags = target_div.find_all("a")

        level3_path =  a_tags[-2].text.strip()
        level4_path =  a_tags[-1].text.strip()
        return f"/{level3_path}/{level4_path}"

    def get_title(self):
        """
        获取标题
        :return:
        """
        title = self.html_content.find("div", {"class": "AfficheTitle"}).text.strip()
        title = title.replace('\r\n', '')  # 去掉换行符
        title = ' '.join(title.split())  # 去掉多余的空格
        return title


    def is_process_announcement(self, content: str) -> bool:
        keyword = ["中标结果公告", "中标公告"]

        return any(key in content for key in keyword)

    def is_process_pre_announcement(self, content: str) -> bool:
        keyword = ["中标前公示"]
        return any(key in content for key in keyword)

    def get_file_description(self, file_info):
        file_url = file_info["url"]
        file_name = file_info["name"].strip()

        return file_url, file_name

