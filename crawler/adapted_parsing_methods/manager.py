class CrawlStrategyManager:
    def __init__(self):
        self.strategies = {}

    def register_strategy(self, domain, strategy_function):
        """注册一个域名和对应的爬取策略"""
        self.strategies[domain] = strategy_function

    def get_strategy(self, domain):
        """获取指定域名的爬取策略"""
        return self.strategies.get(domain, None)

# 示例爬取策略
def fetch_ggzy_qz(html_content):
    # 针对 ggzy.qz.gov.cn 的爬取策略
    return f"Fetched data from ggzy.qz.gov.cn: {html_content[:100]}"

def fetch_ggzyjy_jinhua(html_content):
    # 针对 ggzyjy.jinhua.gov.cn 的爬取策略
    return f"Fetched data from ggzyjy.jinhua.gov.cn: {html_content[:100]}"
