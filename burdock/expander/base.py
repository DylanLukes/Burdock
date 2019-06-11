from abc import ABC
from typing import AnyStr

import pandas as pd
from pandas import Series, DataFrame

__all__ = [
    'Expander'
]


class Expander(ABC):
    tag: AnyStr

    def __init__(self, tag):
        self.tag = tag

    def get_tag(self):
        return self.tag

    def expand_columns(self, series: Series) -> DataFrame:
        return pd.DataFrame()

    def expand_constants(self, series: Series) -> DataFrame:
        return pd.DataFrame()
