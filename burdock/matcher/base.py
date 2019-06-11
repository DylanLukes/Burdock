from abc import ABC, abstractmethod
from typing import AnyStr, Type, SupportsFloat, Callable

from pandas import Series
from pandas.core.dtypes.common import infer_dtype_from_object

__all__ = [
    'matcher',
    'Matcher',
    'DataTypeMatcher',
    'ProbabilisticMatcher'
]


class Matcher(ABC):
    """A simple class for defining a matcher."""

    tag: AnyStr

    def __init__(self, tag):
        self.tag = tag

    def __call__(self, *args, **kwargs):
        return self.match(*args, **kwargs)

    def get_tag(self):
        return self.tag

    @abstractmethod
    def match(self, series: Series) -> bool:
        pass


class FunctionMatcher(Matcher):
    match_func: Callable[[Series], bool]

    def __init__(self, tag, match_func: Callable[[Series], bool]):
        super().__init__(tag)
        self.match_func = match_func

    def match(self, series: Series) -> bool:
        return self.match_func(series)


def matcher(tag):
    def matcher_decorator(func):
        m = FunctionMatcher(tag, func)
        return m
    return matcher_decorator


class DataTypeMatcher(Matcher):
    dtype: Type

    def __init__(self, tag, dtype):
        super().__init__(tag)
        self.dtype = dtype

    @staticmethod
    def normalize_dtype(dtype):
        return infer_dtype_from_object(dtype)

    def get_dtypes(self):
        return self.dtype

    def match(self, series: Series) -> bool:
        this_dtype = self.normalize_dtype(self.dtype)
        that_dtype = self.normalize_dtype(series.dtype)
        return this_dtype == that_dtype


class ProbabilisticMatcher(Matcher):
    threshold: SupportsFloat

    def get_threshold(self) -> float:
        return float(self.threshold)

    @abstractmethod
    def match_prob(self, series: Series) -> SupportsFloat:
        pass

    def match(self, series: Series) -> bool:
        p = float(series.match_prob(series))
        t = self.get_threshold()
        return p > t
