class Metrics:
    def __init__(self):
        self.l1_hits = 0
        self.l2_hits = 0
        self.cache_misses = 0
        self.l1_evictions = 0

    def to_dict(self):
        return {
            "l1_hits": self.l1_hits,
            "l2_hits": self.l2_hits,
            "cache_misses": self.cache_misses,
            "l1_evictions": self.l1_evictions
        }


metrics = Metrics()
