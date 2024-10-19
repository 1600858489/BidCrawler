import os

import pandas as pd
from html2text import html2text

from config import DEBUG
from core.history_manager import HistoryManager
from log.logger import Logger
from .qz import QzParser

log = Logger().get_logger()

history_manager = HistoryManager()


class JiaxingParser(QzParser):
    """
    JiaxingParser inherits from QzParser.
    url: http://jxszwsjb.jiaxing.gov.cn
    """
    def parse_html(self):
        target_div = self.html_content.find('div', {'class': 'ewb-bulid-items'})
        res = []
        for item in target_div.find_all('a'):
            url = self.scheme + "://" + self.domain + item.get('href')
            res.append((1, url, "table"))
            if DEBUG:
                # break
                pass
        self.response_type = "url_list"
        self.response = res


    def save_announcement(self,file_path):
        table = self.html_content.find('table', border="1")

        data = []
        header = []
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            header.append(cells[0].text)
            data.append(cells[1].text)
        data= [data]
        df = pd.DataFrame(data, columns=header)
        output_file = file_path + "/" + "中标结果公告.csv"
        if os.path.exists(output_file):
            df.to_csv(output_file, mode='a', header=False, index=False)
        else:
            df.to_csv(output_file, index=False,encoding='utf-8-sig')

        log.info("Saved announcement to file: " + output_file)
        return True


    def get_file_info(self):
        file_info = self.html_content.find_all('a',href=True)
        res = [i for i in file_info if "cmd=download" in i.get('href')]
        print(res)
        return res


    def get_content(self):
        content = self.html_content.find('div',class_='zoom')
        if not content:
            content = ""
        content = html2text(str(content))
        return content
