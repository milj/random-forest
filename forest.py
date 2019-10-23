from tree import build_tree, entropy


class Forest:
    def __init__(self, size, columns, target_column, rows):
        self._tree = build_tree(
            columns=columns,
            target_column=target_column,
            rows=rows,
            score_function=entropy,
        )
        print(self._tree)

    def classify(self, row):
        return self._tree.classify(row).normalized()
