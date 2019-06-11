from collections import defaultdict
from enum import Enum
from itertools import chain
from typing import Collection, AnyStr, Dict, Set, Iterable, Union, Optional

import pandas as pd
from pandas import DataFrame, Series
from pandas.core.dtypes.common import is_float_dtype, is_integer_dtype, is_bool_dtype, is_string_dtype

from burdock.matcher import Matcher
from burdock.matcher.common import numeric_matcher, float_matcher, integer_matcher, string_matcher
from burdock.expander import Expander
from burdock.expander.common import statistics_expander


class DaikonType(Enum):
    integer = 'int'
    float = 'float'
    boolean = 'boolean'
    string = 'java.lang.String'

    @staticmethod
    def from_dtype(dtype):
        if is_integer_dtype(dtype):
            return DaikonType.integer
        if is_float_dtype(dtype):
            return DaikonType.float
        if is_bool_dtype(dtype):
            return DaikonType.boolean
        if is_string_dtype(dtype):
            return DaikonType.string

    def __str__(self):
        return self.value


class DaikonVariable:
    name: str
    var_kind: str
    rep_type: DaikonType
    dec_type: str
    comparability: Optional[int]

    constant_value = None

    def __init__(self, name: str, rep_type: DaikonType, dec_type: str = None, constant_value=None):
        self.name = name
        self.var_kind = 'variable'
        self.rep_type = rep_type
        if dec_type:
            self.dec_type = dec_type
        else:
            self.dec_type = rep_type.name
        self.comparability = None
        self.constant_value = constant_value

    def is_constant(self):
        return self.constant_value is not None

    def __str__(self):
        if self.is_constant():
            return "const {name} : {dec_type}/{rep_type} = {value}".format(
                name=self.name,
                dec_type=self.dec_type,
                rep_type=self.rep_type,
                value=self.constant_value
            )
        else:
            return "var {name} : {dec_type}/{rep_type}".format(
                name=self.name,
                dec_type=self.dec_type,
                rep_type=self.rep_type,
            )

    @staticmethod
    def from_df(df: DataFrame, as_constants=False) -> Series:
        return Series({
            name: DaikonVariable(name, DaikonType.from_dtype(dtype),
                                 constant_value=df[name].iloc[0] if as_constants else None)
            for name, dtype in df.dtypes.iteritems()
        })


class Burdock:
    DEFAULT_MATCHERS: Collection[Matcher] = [
        numeric_matcher,
        float_matcher,
        integer_matcher,
        string_matcher
    ]

    DEFAULT_EXPANDERS: Collection[Expander] = [
        statistics_expander
    ]

    name: str

    # todo: init variables from provided dataframe.
    variables: Series
    traces: DataFrame

    latent_variables: Series
    latent_traces: DataFrame

    _matchers: Dict[str, Collection[Matcher]] = defaultdict(set)
    _expanders: Dict[str, Collection[Expander]] = defaultdict(set)

    matched_tags: Dict[str, Set[str]] = defaultdict(set)

    def __init__(self, name: AnyStr, df: DataFrame, matchers=None, expanders=None):
        self.name = str(name)

        self.variables = DaikonVariable.from_df(df)
        self.traces = df

        self.latent_variables = Series()
        self.latent_traces = DataFrame()

        if matchers is None:
            matchers = self.DEFAULT_MATCHERS

        for matcher in matchers:
            self.add_matcher(matcher)

        if expanders is None:
            expanders = self.DEFAULT_EXPANDERS

        for expander in expanders:
            self.add_expander(expander)

    @property
    def matchers(self) -> Iterable[Matcher]:
        return chain(*self._matchers.values())

    def get_matchers(self, tag: AnyStr) -> Iterable[Matcher]:
        return self._matchers.get(str(tag), [])

    def add_matcher(self, matcher: Matcher):
        self._matchers[matcher.tag] |= {matcher}

    @property
    def expanders(self) -> Iterable[Expander]:
        return chain(*self._expanders.values())

    def get_expanders(self, tag: AnyStr) -> Iterable[Expander]:
        return self._expanders.get(str(tag), [])

    def add_expander(self, expander: Expander):
        self._expanders[expander.tag] |= {expander}

    def match(self):
        for column_id in self.traces.columns:
            column: Series = self.traces[column_id]
            tags: Set[str] = set()

            for matcher in self.matchers:
                if matcher.match(column):
                    tags.add(matcher.tag)
                    print("Tagged column {} with '{}'.".format(column_id, matcher.tag))

            self.matched_tags[column_id] = tags

    def expand(self):
        for column_id in self.traces.columns:
            column: Series = self.traces[column_id]

            for tag in self.matched_tags[column_id]:
                for expander in self.get_expanders(tag):
                    constants = expander.expand_constants(column)
                    self.latent_variables = pd.concat([
                        self.latent_variables,
                        DaikonVariable.from_df(constants, as_constants=True)
                    ])

                    columns = expander.expand_columns(column)
                    self.latent_variables = pd.concat([self.latent_variables, DaikonVariable.from_df(columns)])
                    self.latent_traces = pd.concat([self.latent_traces, columns])
