class QueueUI:
    def __init__(self, queue, domain, level):
        self.queue = queue
        self.domain = domain
        self.level = level

    def __str__(self):
        return f"QueueUI(queue={self.queue}, domain={self.domain}, level={self.level})"
