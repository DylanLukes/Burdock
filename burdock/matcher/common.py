from pandas import Series
from pandas.core.dtypes.common import is_numeric_dtype, is_float_dtype, is_integer_dtype, is_string_dtype

from .base import matcher

__all__ = [
    'numeric_matcher',
    'float_matcher',
    'integer_matcher',
    'string_matcher'
]


@matcher(tag='type.numeric')
def numeric_matcher(series: Series) -> bool:
    return is_numeric_dtype(series)


@matcher(tag='type.numeric.float')
def float_matcher(series: Series) -> bool:
    return is_float_dtype(series)


@matcher(tag='type.numeric.integer')
def integer_matcher(series: Series) -> bool:
    return is_integer_dtype(series)


@matcher(tag='type.string')
def string_matcher(series: Series) -> bool:
    return is_string_dtype(series)
