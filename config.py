import os

def set_directory(directory):
    file_path = os.path.join(os.getcwd(), directory)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    return file_path


LOG_PATH = set_directory('logs')
FILE_PATH = set_directory("downloads")

