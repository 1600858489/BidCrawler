from .adapted_parsing_methods.manager import *

class WebCrawler:
    def __init__(self):
        self.crawl_strategy_manager = CrawlStrategyManager()

    def fetch(self, url, level=1, keyword=None,max_day=30):
        if "ggzy.qz.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("ggzy.qz.gov.cn")
        elif "ggzyjy.jinhua.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("ggzyjy.jinhua.gov.cn")
        elif "ggzy.hzctc.hangzhou.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("ggzy.hzctc.hangzhou.gov.cn")
        elif "ggzyjy-eweb.wenzhou.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("ggzyjy-eweb.wenzhou.gov.cn")
        elif "jxszwsjb.jiaxing.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("jxszwsjb.jiaxing.gov.cn")
        elif "ggzyjy.huzhou.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("ggzyjy.huzhou.gov.cn")
        elif "zsztb.zhoushan.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("zsztb.zhoushan.gov.cn")
        elif "ggzy.tzztb.zjtz.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("ggzy.tzztb.zjtz.gov.cn")
        elif "lssggzy.lishui.gov.cn" in str(url):
            strategy = self.crawl_strategy_manager.get_strategy("lssggzy.lishui.gov.cn")


        else:
            return False, None
        # 模拟获取页面内容
        res = strategy(url, level, keyword,max_day)
        if res is None:
            return False, None
        return True, res
