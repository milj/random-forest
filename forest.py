#!/bin/python3

import argparse
import csv
from itertools import groupby
from math import log
import sys


OPERATIONS = {
    '==': lambda x, a: x == a,
    # numbers only:
    '>' : lambda x, a: x > a,
    '<': lambda x, a: x < a,
}

def operations_for(value):
    if isinstance(value, (int, float)):
        return ('==', '>', '<')
    elif isinstance(value, str):
        return ('==',)
    else:
        return ()

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

def entropy(rows, column):
    result = 0
    for (value, count) in value_counts(rows, column).items():
        p = count / len(rows)
        result -= p * log(p)
    return result

def value_counts(rows, column):
    values = [row[column] for row in rows]
    return {x[0]: len(list(x[1])) for x in groupby(sorted(values))}

def partition(rows, column, operation, pivot):
    return (
        [row for row in rows if OPERATIONS[operation](row[column], pivot)],
        [row for row in rows if not OPERATIONS[operation](row[column], pivot)]
    )

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

def print_tree(node, level=0):
    indent = '  ' * level
    if node.values:
        print(indent + str(node.values))
    else:
        print(indent + '{} {} {} ?'.format(node.column, node.operation, node.pivot))
        print(indent + 'T:')
        print_tree(node.positive_branch, level + 1)
        print(indent + 'F:')
        print_tree(node.negative_branch, level + 1)

def main(args):
    parser = argparse.ArgumentParser(description='Random forest predictor')
    parser.add_argument(
        'dataset_file',
        help='CSV file containing the input dataset file',
        metavar='dataset_file',
        type=argparse.FileType('r'),
    )
    parser.add_argument(
        '--target_column',
        help='Name of the dataset column to be predicted (default: last column)',
        metavar='target_column',
        type=str,
    )
    args = parser.parse_args(args)

    data_rows = [row for row in csv.DictReader(args.dataset_file, delimiter=',', quotechar='"')]
    assert len(data_rows) > 0

    data_columns = list(data_rows[0].keys())

    target_column = args.target_column or data_columns[-1]
    assert target_column in data_columns

    for column in data_columns:
        if column.endswith('!int'):
            for row in data_rows:
                row[column] = int(row[column])
        if column.endswith('!float'):
            for row in data_rows:
                row[column] = float(row[column])

    tree = build_tree(
        columns=data_columns,
        target_column=target_column,
        rows=data_rows,
        score_function=entropy,
    )

    print_tree(tree)


if __name__ == '__main__':
    main(sys.argv[1:])
