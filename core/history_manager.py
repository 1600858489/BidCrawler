import os

import pandas as pd


class HistoryManager:
    def __init__(self, csv_file='history.csv'):
        self.csv_file = csv_file
        # 如果 CSV 文件不存在，创建一个新的 DataFrame
        if not os.path.exists(self.csv_file):
            self.history_df = pd.DataFrame(
                columns=['url', 'has_attachment', 'attachment_path', 'platform', 'timestamp', 'description'])
            self.history_df.to_csv(self.csv_file, index=False)  # 创建 CSV 文件
        else:
            self.history_df = pd.read_csv(self.csv_file)  # 读取现有的 CSV 文件

    def add_to_history(self, url, has_attachment, attachment_path, platform, timestamp, description):
        # 创建一个新记录
        new_record = {
            'url': url,
            'has_attachment': has_attachment,
            'attachment_path': attachment_path,
            'platform': platform,
            'timestamp': timestamp,
            'description': description
        }

        # 将新记录转换为 DataFrame
        new_record_df = pd.DataFrame([new_record])

        # 使用 pd.concat() 来添加新记录
        self.history_df = pd.concat([self.history_df, new_record_df], ignore_index=True)

        # 将 DataFrame 写入 CSV 文件
        self.history_df.to_csv(self.csv_file, index=False)

    def is_in_history(self, url):
        return not self.history_df[self.history_df['url'] == url].empty

    def get_history(self):
        return self.history_df



# 使用示例
if __name__ == '__main__':
    history_manager = HistoryManager()

    # 添加新记录
    history_manager.add_to_history(
        'http://example.com',
        True,
        '/path/to/attachment',
        'example_platform',
        '2024-10-05 10:00:00',  # 时间戳示例
        '这是一个示例描述'  # 描述示例
    )

    # 检查是否在历史记录中
    print(history_manager.is_in_history('http://example.com'))  # 输出 True

    # 获取历史记录
    print(history_manager.get_history())
