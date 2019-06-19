from collections import defaultdict
from itertools import chain
from typing import Collection, Dict, Set, AnyStr, Iterable, TextIO

import pandas as pd
from pandas import Series, DataFrame

import jinja2 as j2

from burdock.core.variable import DaikonVariable, consts_from_df, vars_from_df
from burdock.expander import Expander
from burdock.matcher import Matcher


def _daikon_format_filter(var: DaikonVariable, value=None):
    if value is None:
        assert var.constant_value is not None
        value = var.constant_value

    if var.is_integer or var.is_float:
        return "{}".format(value)
    elif var.is_boolean:
        return "{}".format(1 if value else 0)
    elif var.is_string:
        return "\"{}\"".format(value)


class Burdock:
    name: str

    variables: Dict[str, DaikonVariable]
    traces: DataFrame

    latent_variables: Dict[str, DaikonVariable]
    latent_traces: DataFrame

    _matchers: Dict[str, Collection[Matcher]]
    _expanders: Dict[str, Collection[Expander]]

    _matched_tags: Dict[str, Set[str]] = defaultdict(set)

    _template_env = j2.Environment(loader=j2.PackageLoader('burdock.core', 'templates'))
    _template_env.filters['daikon'] = _daikon_format_filter

    _decls_template = _template_env.get_template('decls.jinja2')
    _dtrace_template = _template_env.get_template('dtrace.jinja2')

    def __init__(self, name: AnyStr, df: DataFrame, matchers=None, expanders=None):
        self.name = str(name)

        self.variables = vars_from_df(df)
        self.traces = df

        self.latent_variables = dict()
        self.latent_traces = DataFrame()

        self._matchers: Dict[str, Collection[Matcher]] = defaultdict(set)
        if matchers is None:
            matchers = []
        for matcher in matchers:
            self.add_matcher(matcher)

        self._expanders: Dict[str, Collection[Expander]] = defaultdict(set)
        if expanders is None:
            expanders = []
        for expander in expanders:
            self.add_expander(expander)

    def get_variable(self, column_label: str):
        if column_label in self.variables:
            return self.variables[column_label]
        if column_label in self.latent_variables:
            return self.latent_variables[column_label]

    @property
    def matchers(self) -> Iterable[Matcher]:
        return chain(*self._matchers.values())

    def get_matchers(self, tag: AnyStr) -> Iterable[Matcher]:
        return self._matchers.get(str(tag), [])

    def add_matcher(self, matcher: Matcher):
        self._matchers[matcher.tag] |= {matcher}

    def match(self):
        for column_id in self.traces.columns:
            column: Series = self.traces[column_id]
            tags: Set[str] = set()

            for matcher in self.matchers:
                if matcher.match(column):
                    tags.add(matcher.tag)
                    print("Tagged column {} with '{}'.".format(column_id, matcher.tag))

            self._matched_tags[column_id] = tags

    @property
    def expanders(self) -> Iterable[Expander]:
        return chain(*self._expanders.values())

    def get_expanders(self, tag: AnyStr) -> Iterable[Expander]:
        return self._expanders.get(str(tag), [])

    def add_expander(self, expander: Expander):
        self._expanders[expander.tag] |= {expander}

    def expand(self):
        for column_id in self.traces.columns:
            column: Series = self.traces[column_id]

            for tag in self._matched_tags[column_id]:
                for expander in self.get_expanders(tag):
                    const_df = expander.expand_constants(column)
                    self.latent_variables.update(consts_from_df(const_df))

                    vars_df = expander.expand_variables(column)
                    self.latent_variables.update(vars_from_df(vars_df))
                    self.latent_traces = pd.concat([self.latent_traces, vars_df])

    def write_decls(self, out: TextIO):
        template_data = {
            'name': self.name,
            'variables': [
                var
                for var
                in chain(self.variables.values(),
                         self.latent_variables.values())
            ]
        }

        decls_text = self._decls_template.render(template_data)
        out.write(decls_text)

    def write_dtrace(self, out: TextIO):
        template_data = {
            'name': self.name,
            'traces': [
                [
                    {
                        'label': label,
                        'var': self.get_variable(label),
                        'value': row[label]
                    }
                    for label
                    in chain(self.traces.columns,
                             self.latent_traces.columns)
                ]
                for (i, row)
                in chain(self.traces.iterrows(),
                         self.latent_traces.iterrows())
            ]
        }

        dtrace_text = self._dtrace_template.render(template_data)
        out.write(dtrace_text)
