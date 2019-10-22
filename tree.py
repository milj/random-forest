from itertools import groupby
from math import log


OPERATIONS = {
    '==': lambda x, a: x == a,
    # numbers only:
    '<': lambda x, a: x < a,
    '>': lambda x, a: x > a,
}

def operations_for(value):
    if isinstance(value, (int, float)):
        return ('<', '>', '==')
    elif isinstance(value, str):
        return ('==',)
    else:
        return ()

def entropy(rows, column):
    result = 0
    for (value, count) in value_counts(rows, column).items():
        p = count / len(rows)
        result -= p * log(p)
    return result

def gini_impurity(rows, column):
    return 0 # TODO

def value_counts(rows, column):
    values = [row[column] for row in rows]
    return {x[0]: len(list(x[1])) for x in groupby(sorted(values))}

def partition(rows, column, operation, pivot):
    return (
        [row for row in rows if OPERATIONS[operation](row[column], pivot)],
        [row for row in rows if not OPERATIONS[operation](row[column], pivot)]
    )

class Node:
    def __init__(self, **kwargs):
        if 'values' in kwargs:
            # leaf
            assert all([
                key not in kwargs for key in
                ['column', 'operation', 'pivot', 'positive_branch', 'negative_branch']
            ])
            self.values = kwargs.get('values')
        else:
            # inner node
            assert 'values' not in kwargs
            self.values = None
            self.column = kwargs.get('column')
            self.operation = kwargs.get('operation')
            assert self.operation in OPERATIONS.keys()
            self.pivot = kwargs.get('pivot')
            self.positive_branch = kwargs.get('positive_branch')
            self.negative_branch = kwargs.get('negative_branch')

    def __str__(self, level=0):
        indent = '  ' * level
        result = ''
        def append(s):
            nonlocal result
            result += indent + s + '\n'
        if self.values:
            append(str(self.values))
        else:
            append('{} {} {} ?'.format(self.column, self.operation, self.pivot))
            append('T:')
            result += self.positive_branch.__str__(level + 1)
            append('F:')
            result += self.negative_branch.__str__(level + 1)
        return result

    def classify(self, row):
        if self.values:
           return self.values
        else:
            if OPERATIONS[self.operation](row[self.column], self.pivot):
                return self.positive_branch.classify(row)
            else:
                return self.negative_branch.classify(row)

def build_tree(columns, target_column, rows, score_function):
    if not rows:
        return Node(values={})

    best_partition = {}
    score = score_function(rows, target_column)

    for column in [column for column in columns if column != target_column]:
        column_value_set = {row[column] for row in rows}
        assert (
            # all values have the same operations
            len({operations_for(value) for value in column_value_set}) == 1
        )

        for operation in operations_for(next(iter(column_value_set))):
            for pivot in column_value_set:
                positive_rows, negative_rows = partition(rows, column, operation, pivot)
                score_gain = (
                    score
                    - (len(positive_rows) / len(rows)) * score_function(positive_rows, target_column)
                    - (len(negative_rows) / len(rows)) * score_function(negative_rows, target_column)
                )

                if score_gain > best_partition.get('score_gain', 0.0):
                    best_partition = {
                        'score_gain': score_gain,
                        'column': column,
                        'operation': operation,
                        'pivot': pivot,
                        'positive_rows': positive_rows,
                        'negative_rows': negative_rows,
                    }

    if best_partition.get('score_gain', 0) > 0:
        return Node(
            column=best_partition['column'],
            operation=best_partition['operation'],
            pivot=best_partition['pivot'],
            positive_branch=build_tree(
                columns=columns,
                target_column=target_column,
                rows=best_partition['positive_rows'],
                score_function=score_function
            ),
            negative_branch=build_tree(
                columns=columns,
                target_column=target_column,
                rows=best_partition['negative_rows'],
                score_function=score_function
            ),
        )
    else:
        return Node(
            values=value_counts(rows, target_column),
        )
