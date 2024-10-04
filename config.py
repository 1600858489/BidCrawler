import os


def set_download_directory(directory):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), directory)
    print(file_path)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    return file_path


FILE_PATH = set_download_directory("downloads")
