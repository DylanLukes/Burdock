import argparse
from os import path
import sys

import numpy as np
import pandas as pd

from pandas import DataFrame, Series

from jinja2 import Environment, PackageLoader, Template

parser = argparse.ArgumentParser(description='Produce .dtrace and .decls for a given CSV/TSV file.')
parser.add_argument('input_file',
                    metavar='file',
                    type=argparse.FileType('r', encoding='utf-8'))
parser.add_argument('--out-decls',
                    dest='output_decls_file',
                    metavar='decls',
                    type=argparse.FileType('w+', encoding='utf-8'))

def dec_type(dtype):
    if dtype == np.int64:
        return 'int'
    if dtype == np.float64:
        return 'double'
    if dtype == bool:
        return 'boolean'
    if dtype == object:
        return 'java.lang.String'
    raise RuntimeError("Unsupported dtype: %s".format(repr(dtype)))

def rep_type(dtype):
    if dtype == np.int64:
        return 'int'
    if dtype == np.float64:
        return 'double'
    if dtype == bool:
        return 'boolean'
    if dtype == object:
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

def main(argv):
    args = parser.parse_args()
    input_file = args.input_file
    input_path = path.normpath(input_file.name)
    input_dirname, input_filename = path.split(input_path)

    df: DataFrame = pd.read_csv(args.input_file)
    name = path.splitext(input_filename)[0]

    output_decls_file = args.output_decls_file
    if not output_decls_file:
        output_decls_path = path.join(input_dirname, name + '.decls')
        output_decls_file = open(output_decls_path, 'w+')

    output_decls(df, name, output_decls_file)

if __name__ == '__main__':
    main(sys.argv)