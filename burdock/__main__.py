import argparse
import os
import sys

import numpy as np
import pandas as pd

from pandas import DataFrame, Series

from jinja2 import Environment, PackageLoader, Template

parser = argparse.ArgumentParser(description='Produce .dtrace and .decls for a given CSV/TSV file.')
parser.add_argument('input', metavar='input', type=argparse.FileType('r', encoding='utf-8'))


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

def main(argv):
    args = parser.parse_args()

    df: DataFrame = pd.read_csv(args.input)
    input_name = os.path.splitext(os.path.basename(os.path.normpath(args.input.name)))[0]

    template_env: Environment = Environment(loader=PackageLoader('burdock', 'templates'))
    template: Template = template_env.get_template('decls.jinja2')

    template_data = {
        'name': input_name,
        'variables': []
    }
    for col_id in df:
        column: Series = df[col_id]

        template_data['variables'].append({
            'name': column.name,
            'dec_type': dec_type(column.dtype),
            'rep_type': rep_type(column.dtype)
        })

    print(template.render(template_data))



if __name__ == '__main__':
    main(sys.argv)
