import requests
from bs4 import BeautifulSoup

class WebCrawler:
    def fetch(self, url):
        """请求网页并返回解析后的页面内容"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            raise Exception(f"请求失败：{e}")

    def extract_links(self, html):
        """提取所有的链接"""
        soup = BeautifulSoup(html, 'html.parser')
        return [link['href'] for link in soup.find_all('a', href=True)]
