from itertools import groupby
from math import ceil, sqrt
from random import choices, choice, randint, sample

from tree import build_tree


class Forest:
    def __init__(self, columns, target_column, rows, forest_size=None):
        if not forest_size:
            forest_size = ceil(sqrt(len(rows)))

        bag_size = ceil(len(rows) / forest_size)

        self._trees = [
            build_tree(
                columns=sample(columns, randint(min(2, len(columns)), len(columns))),
                target_column=target_column,
                rows=choices(rows, k=bag_size), # with replacement
                score_type=choice(('entropy', 'gini')),
                # TODO min_gain_for_split=
            )
            for _ in range(forest_size)
        ]

        for tree in self._trees:
            print('-' * 80)
            print(tree)

    def classify(self, row):
        outputs = [tree.classify(row).normalized() for tree in self._trees]
        most_probable_values = [sorted(o.items(), key=lambda o: o[1])[-1][0] for o in outputs]
        # return the most frequent from most_probable_values
        return sorted(
            {x[0]: len(list(x[1])) for x in groupby(sorted(most_probable_values))}.items(),
            key=lambda x: x[1]
        )[-1][0]
