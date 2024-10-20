import os

def set_directory(directory):
    file_path = os.path.join(os.getcwd(), directory)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    return file_path



VERSION = "v1.1.1"
LOG_PATH = set_directory('logs')
FILE_PATH = set_directory("downloads")
PLATFORM_HASH = {

}

CSV_PATH = os.path.join(FILE_PATH, "中标结果.csv")

DEBUG = True

