import os

def set_directory(directory):
    file_path = os.path.join(os.getcwd(), directory)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    return file_path



VERSION = "v1.1.1"
LOG_PATH = set_directory('logs')
FILE_PATH = set_directory("downloads")

BASE_DIR = os.getcwd()


PLATFORM_HASH = {
    "ggzy.qz.gov.cn": "衢州",
    "ggzyjy.jinhua.gov.cn": "金华",
    "ggzy.hzctc.hangzhou.gov.cn": "杭州",
    "ggzyjy-eweb.wenzhou.gov.cn": "温州",
    "jxszwsjb.jiaxing.gov.cn": "嘉兴",
    "ggzyjy.huzhou.gov.cn": "湖州",
    "zsztb.zhoushan.gov.cn": "舟山",
    "ggzy.tzztb.zjtz.gov.cn": "台州",
    "lssggzy.lishui.gov.cn": "丽水"
}

ANNOUNCEMENT_PATH = os.path.join(FILE_PATH, "中标结果.csv")
PRE_ANNOUNCEMENT_PATH = os.path.join(FILE_PATH, "预中标结果.csv")
CONFIG_PATH = os.path.join(os.getcwd(), "config.json")

DEBUG = True

