from abc import ABC, abstractmethod
from typing import SupportsFloat, Callable

from pandas import Series

__all__ = [
    'matcher',
    'Matcher',
    'ProbabilisticMatcher'
]


class Matcher(ABC):
    """A simple class for defining a matcher."""

    def __init__(self, tag: str):
        self.tag = tag

    def __call__(self, *args, **kwargs):
        return self.match(*args, **kwargs)

    def get_tag(self):
        return self.tag

    @abstractmethod
    def match(self, series: Series) -> bool:
        pass


class FunctionMatcher(Matcher):
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


class ProbabilisticMatcher(Matcher):

    @abstractmethod
    def get_threshold(self) -> float:
        pass

    @abstractmethod
    def match_prob(self, series: Series) -> SupportsFloat:
        pass

    def match(self, series: Series) -> bool:
        p = float(series.match_prob(series))
        t = self.get_threshold()
        return p > t
