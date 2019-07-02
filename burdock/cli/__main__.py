import argparse
from io import TextIOWrapper
from os import path

import pandas as pd
from pandas import DataFrame

from burdock.core import Burdock
from burdock.util.subprocess import run_daikon

# todo: use `constant` flag in decls to avoid output in traces.

# todo: mark synthetic/derived/latent variables in decls var flags.
# todo: use valid-values for categorical data.

# todo: invent our own new flags...?

parser = argparse.ArgumentParser(description='Produce .dtrace and .decls for a given CSV/TSV file.')
parser.add_argument('input_file',
                    metavar='path',
                    type=argparse.FileType('r', encoding='utf-8'))
parser.add_argument('--out-decls',
                    dest='output_decls_file',
                    metavar='path',
                    type=argparse.FileType('w+', encoding='utf-8'))
parser.add_argument('--out-dtrace',
                    dest='output_dtrace_file',
                    metavar='path',
                    type=argparse.FileType('w+', encoding='utf-8'))
parser.add_argument('--verbose',
                    dest='verbose',
                    default=False,
                    type=bool)
parser.add_argument('--run-daikon',
                    dest='run_daikon',
                    default=False,
                    type=bool)


def main(args):
    input_file: TextIOWrapper = args.input_file
    input_path = path.normpath(input_file.name)
    input_dirname, input_filename = path.split(input_path)

    df: DataFrame = pd.read_csv(args.input_file)
    name = path.splitext(input_filename)[0]

    b = Burdock(name, df)
    # b.add_matcher(numeric_matcher)
    # b.add_expander(statistics_expander)

    b.match()
    b.expand()

    if args.verbose:
        print("\nVariables:\n{}\n".format(b.variables))
        print("\nTraces:\n{}\n".format(b.traces))
        print("\nLatent Variables:\n{}\n".format(b.latent_variables))
        print("\nLatent Traces:\n{}\n".format(b.latent_traces))

    # Decls
    output_decls_file = args.output_decls_file
    if not output_decls_file:
        output_decls_path = path.join(input_dirname, name + '.decls')
        output_decls_file = open(output_decls_path, 'w+')

    b.write_decls(output_decls_file)
    output_decls_file.flush()

    # Dtrace
    output_dtrace_file = args.output_dtrace_file
    if not output_dtrace_file:
        output_dtrace_path = path.join(input_dirname, name + '.dtrace')
        output_dtrace_file = open(output_dtrace_path, 'w+')

    b.write_dtrace(output_dtrace_file)
    output_dtrace_file.flush()

    if args.run_daikon:
        run_daikon(path.abspath(output_decls_file.name), path.abspath(output_dtrace_file.name))


def entry():
    args = parser.parse_args()
    main(args)


if __name__ == '__main__':
    entry()
