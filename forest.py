#!/bin/python3

import argparse
import csv
import sys
from tree import build_tree, entropy


def type_cast(rows, columns):
    castings = {'!int': int, '!float': float}
    for column in columns:
        for suffix, function in castings.items():
            if column.endswith(suffix):
                for row in rows:
                    row[column] = function(row[column])

def main(args):
    parser = argparse.ArgumentParser(description='Random forest predictor')
    parser.add_argument(
        'training_dataset',
        help='CSV file containing the training dataset file',
        metavar='training_dataset',
        type=argparse.FileType('r'),
    )
    parser.add_argument(
        'test_dataset',
        help='CSV file containing the test dataset file',
        metavar='test_dataset',
        type=argparse.FileType('r'),
    )
    parser.add_argument(
        '--target_column',
        help='Name of the target dataset column (default: last column)',
        metavar='target_column',
        type=str,
    )
    args = parser.parse_args(args)

    training_rows = [row for row in csv.DictReader(args.training_dataset, delimiter=',', quotechar='"')]
    assert len(training_rows) > 0

    training_columns = list(training_rows[0].keys())

    target_column = args.target_column or training_columns[-1]
    assert target_column in training_columns

    type_cast(training_rows, training_columns)

    tree = build_tree(
        columns=training_columns,
        target_column=target_column,
        rows=training_rows,
        score_function=entropy,
    )

    print(tree)

    test_rows = [row for row in csv.DictReader(args.test_dataset, delimiter=',', quotechar='"')]
    test_columns = list(test_rows[0].keys())
    type_cast(test_rows, test_columns)

    for row in test_rows:
        print(
            '{} -> {}'.format(
                ', '.join([':'.join((key, str(value))) for (key, value) in list(row.items())]),
                tree.classify(row)
            )
        )


if __name__ == '__main__':
    main(sys.argv[1:])
