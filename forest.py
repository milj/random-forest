#!/bin/python3

import argparse
import csv
import sys
from tree import build_tree, entropy


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

    print(tree)


if __name__ == '__main__':
    main(sys.argv[1:])
