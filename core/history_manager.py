class HistoryManager:
    def __init__(self):
        self.history = set()

    def add_to_history(self, url):
        self.history.add(url)

    def is_in_history(self, url):
        return url in self.history
