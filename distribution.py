class Distribution:
    def __init__(self, value_counts):
        self.value_counts = value_counts
        self._total_count = sum(value_counts.values())

    def normalized(self):
        return {value:count/self._total_count for (value, count) in self.value_counts.items()}

    def __str__(self):
        return str(self.value_counts)

    def __add__(self, x):
        result = self.value_counts.copy()
        for value, count in x.value_counts.items():
            result[value] = result.get(value, 0) + count
        return Distribution(result)
