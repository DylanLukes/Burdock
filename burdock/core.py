from collections import defaultdict
from itertools import chain
from typing import Collection, AnyStr, Dict, Set, Iterable, Union

import pandas as pd
from pandas import DataFrame, Series

from burdock.matcher import Matcher
from burdock.matcher.common import numeric_matcher, float_matcher, integer_matcher, string_matcher
from burdock.expander import Expander
from burdock.expander.common import statistics_expander


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
    df: DataFrame

    expanded_df: DataFrame

    constants: Dict[str, Union[int, float, str, bool]] = dict()

    _matchers: Dict[str, Collection[Matcher]] = defaultdict(set)
    _expanders: Dict[str, Collection[Expander]] = defaultdict(set)

    matched_tags: Dict[str, Set[str]] = defaultdict(set)

    def __init__(self, name: AnyStr, df: DataFrame, matchers=None, expanders=None):
        self.name = str(name)
        self.df = df

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
        for column_id in self.df.columns:
            column: Series = self.df[column_id]
            tags: Set[str] = set()

            for matcher in self.matchers:
                if matcher.match(column):
                    tags.add(matcher.tag)
                    print("Tagged column {} with '{}'.".format(column_id, matcher.tag))

            self.matched_tags[column_id] = tags

    def expand(self):
        self.expanded_df = self.df

        for column_id in self.df.columns:
            column: Series = self.df[column_id]

            for tag in self.matched_tags[column_id]:
                for expander in self.get_expanders(tag):
                    new_constants = expander.expand_constants(column).to_dict()
                    self.constants.update(new_constants)

                    new_columns = expander.expand_columns(column)
                    self.expanded_df = pd.concat([self.expanded_df, new_columns])