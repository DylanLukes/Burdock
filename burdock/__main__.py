import argparse
import sys

import pandas
from pandas import DataFrame

parser = argparse.ArgumentParser(description='Produce .dtrace and .decls for a given CSV/TSV file.')
parser.add_argument('input_path', metavar='input', type=argparse.FileType('r', encoding='utf-8'))


def main(argv):
    args = parser.parse_args()

    frame: DataFrame = pandas.read_csv(args.input_path)

    print(frame.dtypes)
    print(frame.describe())


if __name__ == '__main__':
    main(sys.argv)
