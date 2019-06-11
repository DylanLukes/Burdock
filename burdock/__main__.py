import argparse
from io import TextIOWrapper
from os import path

import numpy as np
import pandas as pd
from jinja2 import Environment, PackageLoader, Template
from pandas import DataFrame, Series
from pandas.core.dtypes.common import is_integer_dtype, is_float_dtype, is_string_dtype, is_bool_dtype

from burdock import Burdock
from burdock.util import run_daikon

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


def dec_type(dtype):
    if is_integer_dtype(dtype):
        return 'int'
    if is_float_dtype(dtype):
        return 'double'
    if is_bool_dtype(dtype):
        return 'boolean'
    if is_string_dtype(dtype):
        return 'java.lang.String'

    raise RuntimeError("Unsupported dtype: %s".format(repr(dtype)))


def rep_type(dtype):
    if is_integer_dtype(dtype):
        return 'int'
    if is_float_dtype(dtype):
        return 'double'
    if is_bool_dtype(dtype):
        return 'boolean'
    if is_string_dtype(dtype):
        return 'java.lang.String'
    raise RuntimeError("Unsupported dtype: %s".format(repr(dtype)))


def output_decls(df, name, output, template_env=Environment(loader=PackageLoader('burdock', 'templates'))):
    template: Template = template_env.get_template('decls.jinja2')

    template_data = {
        'name': name,
        'variables': []
    }
    for col_id in df:
        column: Series = df[col_id]

        template_data['variables'].append({
            'name': column.name,
            'dec_type': dec_type(column.dtype),
            'rep_type': rep_type(column.dtype)
        })

    decls_text = template.render(template_data)

    output.write(decls_text)


def output_dtrace(df, name, output, template_env=Environment(loader=PackageLoader('burdock', 'templates'))):
    template: Template = template_env.get_template('dtrace.jinja2')

    col_types = {}
    for col_id in df:
        col_types[col_id] = rep_type(df[col_id].dtype)

    template_data = {
        'name': name,
        'traces': []
    }
    for (i, row) in df.iterrows():
        trace = []
        for col_id in df.columns:
            trace.append({
                'name': col_id,
                'value': row[col_id],
                'rep_type': col_types[col_id]
            })
        template_data['traces'].append(trace)

    dtrace_text = template.render(template_data)

    output.write(dtrace_text)


def main(args):
    input_file: TextIOWrapper = args.input_file
    input_path = path.normpath(input_file.name)
    input_dirname, input_filename = path.split(input_path)

    df: DataFrame = pd.read_csv(args.input_file)
    name = path.splitext(input_filename)[0]

    description = df.describe()

    b = Burdock(name, df)
    b.match()
    b.expand()

    print("\nVariables:\n{}\n".format(b.variables))
    print("\nTraces:\n{}\n".format(b.traces))
    print("\nLatent Variables:\n{}\n".format(b.latent_variables))
    print("\nLatent Traces:\n{}\n".format(b.latent_traces))

    # for col_id in description:
    #     for stat_id in description.index:
    #         df['{}_{}'.format(col_id, stat_id)] = description[col_id][stat_id]

    # Decls
    output_decls_file = args.output_decls_file
    if not output_decls_file:
        output_decls_path = path.join(input_dirname, name + '.decls')
        output_decls_file = open(output_decls_path, 'w+')

    output_decls(df, name, output_decls_file)

    # Dtrace
    output_dtrace_file = args.output_dtrace_file
    if not output_dtrace_file:
        output_dtrace_path = path.join(input_dirname, name + '.dtrace')
        output_dtrace_file = open(output_dtrace_path, 'w+')

    output_dtrace(df, name, output_dtrace_file)

    output_decls_file.flush()
    output_dtrace_file.flush()

    run_daikon(path.abspath(output_decls_file.name), path.abspath(output_dtrace_file.name))


def entry():
    args = parser.parse_args()
    main(args)


if __name__ == '__main__':
    entry()
