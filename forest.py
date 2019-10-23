from tree import build_tree


class Forest:
    def __init__(self, size, columns, target_column, rows):
        # TODO randomized multiple-tree forest, this is just a single tree stub
        self._trees = [
            build_tree(
                columns=columns,
                target_column=target_column,
                rows=rows,
                score_type='entropy',
            )
            for _ in range(size)
        ]
        print(self._trees[0])

    def classify(self, row):
        return self._trees[0].classify(row).normalized()
