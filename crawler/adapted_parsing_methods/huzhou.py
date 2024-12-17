import datetime
import json
import random
import re
import time

import requests
from html2text import html2text

from core.history_manager import HistoryManager
from log.logger import Logger
from .qz import QzParser

log = Logger().get_logger()

history_manager = HistoryManager()

class HuzhouParser(QzParser):
    """
    HuzhouParser inherits from QzParser and implements its own parsing methods for Huzhou.
    url: https://ggzyjy.huzhou.gov.cn/
    """


    def parse_html(self):
        page_size = 30
        url_list = [
            f"https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=76831&siteid=656&pagesize={page_size}&hasPage=true&pageno=1&callback=jQuery3600405774490577234_1729396308427&_=1729396308429",
            f"https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72450&siteid=656&pagesize={page_size}&hasPage=true&pageno=1&callback=jQuery36007045830106791049_1729396514621&_=1729396514623",
            f"https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72451&siteid=656&pagesize={page_size}&hasPage=true&pageno=1&callback=jQuery3600376028679497344_1729396574069&_=1729396574071",
            f"https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72452&siteid=656&pagesize={page_size}&hasPage=true&pageno=10&callback=jQuery36006892265945618523_1729396779408&_=1729396779410",
            f"https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72453&siteid=656&pagesize={page_size}&hasPage=true&pageno=1&callback=jQuery36009676315929601658_1729396810358&_=1729396810360",
            f"https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72454&siteid=656&pagesize={page_size}&hasPage=true&pageno=1&callback=jQuery36003065541904130671_1729396836192&_=1729396836194",
            f"https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72455&siteid=656&pagesize={page_size}&hasPage=true&pageno=1&callback=jQuery36001858379589293384_1729396874029&_=1729396874031",
            f"https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=75055&siteid=656&pagesize={page_size}&hasPage=true&pageno=1&callback=jQuery360023112751993236258_1729396913364&_=1729396913366",
            f"https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72456&siteid=656&pagesize={page_size}&hasPage=true&pageno=1&callback=jQuery360002169421236702518_1729396945536&_=1729396945538",
            f"https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=75056&siteid=656&pagesize={page_size}&hasPage=true&pageno=1&callback=jQuery36006182659796690959_1729396995940&_=1729396995942"
        ]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
        }
        res = []
        for url in url_list:

            time.sleep(random.randint(1, 3))
            log.info(f"Crawling {url}")
            response = requests.get(url,headers=headers)
            json_strings = re.findall(r'\((.*?)\)', response.text)
            try:
                json_string = json.loads(json_strings[0])
            except Exception as e:
                log.error(f"Failed to parse json string: {json_strings[0]}")
                continue
            for item in json_string["infolist"]:
                url = item["url"]
                name = item["title"]
                date = item["daytime"]
                if history_manager.is_in_history(url):
                    continue
                if self.keyword and self.keyword not in name:
                    continue
                time_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
                if self.max_day and (datetime.datetime.now() - time_obj).days > self.max_day:
                    continue

                res.append((1, url, "detail_page"))
        self.response_type = "url_list"
        self.response = res



    def get_file_info(self):
        file_info = self.html_content.select("a" )
        res = [i for i in file_info if "download" in i.get("href","")]
        return res

    def get_content(self):
        content = self.html_content.select_one("div.container")
        if not content:
            content = "# no data"
        content = html2text(str(content))
        return content

    def is_process_pre_announcement(self, content: str) -> bool:
        keywords = ["中标候选人公示","评标结果公示"]
        return any(keyword in content for keyword in keywords)

    def set_file_path(self):
        target_div = self.html_content.find("div", {"class": "crumbs", "id": "crumbs"})
        tags = target_div.find_all("a")

        try:
            level3_path = tags[-3].text.strip().replace(">", "").strip()
            level4_path = tags[-2].text.strip().replace(">", "").strip()
        except:
            level3_path = "工程建设"
            level4_path = "其他"
        return f"/{level3_path}/{level4_path}"

"""
项目招标计划：https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=76831&siteid=656&pagesize=10&hasPage=true&pageno=1&callback=jQuery3600405774490577234_1729396308427&_=1729396308429
招标文件公示：https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72450&siteid=656&pagesize=10&hasPage=true&pageno=1&callback=jQuery36007045830106791049_1729396514621&_=1729396514623
招标公告：https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72451&siteid=656&pagesize=10&hasPage=true&pageno=1&callback=jQuery3600376028679497344_1729396574069&_=1729396574071
澄清修改信息：https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72452&siteid=656&pagesize=10&hasPage=true&pageno=1&callback=jQuery36006892265945618523_1729396779408&_=1729396779410
开标结果公示：https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72453&siteid=656&pagesize=10&hasPage=true&pageno=1&callback=jQuery36009676315929601658_1729396810358&_=1729396810360
评标结果公示：https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72454&siteid=656&pagesize=10&hasPage=true&pageno=1&callback=jQuery36003065541904130671_1729396836192&_=1729396836194
中标结果公告：https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72455&siteid=656&pagesize=10&hasPage=true&pageno=1&callback=jQuery36001858379589293384_1729396874029&_=1729396874031
评标专家公示：https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=75055&siteid=656&pagesize=10&hasPage=true&pageno=1&callback=jQuery360023112751993236258_1729396913364&_=1729396913366
合同订立信息：https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=72456&siteid=656&pagesize=10&hasPage=true&pageno=1&callback=jQuery360002169421236702518_1729396945536&_=1729396945538
投诉受理及处理结果公告：https://custom.huzhou.gov.cn/hzgov/front/custom/sheng/info/infolist.jsp?cid=75056&siteid=656&pagesize=10&hasPage=true&pageno=1&callback=jQuery36006182659796690959_1729396995940&_=1729396995942
"""