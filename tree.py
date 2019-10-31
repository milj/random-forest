from itertools import groupby

from distribution import Distribution


OPERATIONS = {
    '==': lambda x, a: x == a,
    # numbers only:
    '<': lambda x, a: x < a,
    '>': lambda x, a: x > a,
}

def operations_for(value):
    if isinstance(value, (int, float)):
        return ('<', '>', '==')
    if isinstance(value, str):
        return ('==',)
    return ()

def value_counts(rows, column):
    values = [row[column] for row in rows]
    return {x[0]: len(list(x[1])) for x in groupby(sorted(values))}

def partition(rows, column, operation, pivot):
    return (
        [row for row in rows if row[column] == '' or OPERATIONS[operation](row[column], pivot)],
        [row for row in rows if row[column] == '' or not OPERATIONS[operation](row[column], pivot)]
    )

class Node:
    """A node in a decision tree"""

    def __init__(self, **kwargs):
        if 'distribution' in kwargs:
            # leaf
            assert all([
                key not in kwargs for key in
                ['column', 'operation', 'pivot', 'positive_branch', 'negative_branch']
            ])
            self.distribution = kwargs.get('distribution')
        else:
            # inner node
            assert 'distribution' not in kwargs
            self.distribution = None
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
        if self.distribution:
            append(str(self.distribution))
        else:
            append('{} {} {} ?'.format(self.column, self.operation, self.pivot))
            append('T:')
            result += self.positive_branch.__str__(level + 1)
            append('F:')
            result += self.negative_branch.__str__(level + 1)
        return result

    def classify(self, row):
        """Recursively walk down the tree, select branches according to results of operations stored in the nodes"""

        if self.distribution:
            return self.distribution

        value = row[self.column]
        if value == '':
            return (
                self.positive_branch.classify(row)
                + self.negative_branch.classify(row) # here we are using Distribution's __add__ special method
            )

        if OPERATIONS[self.operation](value, self.pivot):
            return self.positive_branch.classify(row)
        else:
            return self.negative_branch.classify(row)

def build_tree(columns, target_column, rows, score_type):
    """Recursively build a decision tree by finding the best column, value and operation to split on"""

    if not rows:
        return Node(distribution=Distribution({}))

    best_partition = {}
    score = Distribution(value_counts(rows, target_column)).score(score_type)

    for column in [column for column in columns if column != target_column]:
        column_value_set = {row[column] for row in rows} - {''}
        assert (
            # all values have the same operations, or no values
            len({operations_for(value) for value in column_value_set}) <= 1
        )
        if len(column_value_set) == 0:
            continue

        for operation in operations_for(next(iter(column_value_set))):
            for pivot in column_value_set:

                positive_rows, negative_rows = partition(rows, column, operation, pivot)

                score_gain = (
                    score
                    - (len(positive_rows) / len(rows)) * Distribution(
                        value_counts(positive_rows, target_column)
                    ).score(score_type)
                    - (len(negative_rows) / len(rows)) * Distribution(
                        value_counts(negative_rows, target_column)
                    ).score(score_type)
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
                score_type=score_type
            ),
            negative_branch=build_tree(
                columns=columns,
                target_column=target_column,
                rows=best_partition['negative_rows'],
                score_type=score_type
            ),
        )
    else:
        return Node(
            distribution=Distribution(value_counts(rows, target_column))
        )
