from __future__ import annotations

from enum import Enum

from pandas.core.dtypes.common import is_integer_dtype, is_float_dtype, is_bool_dtype, is_string_dtype


class DaikonType(Enum):
    """
    Represents one of Daikon's supported representation types.
    These are Daikon's natively supported types, borrowed from Java.
    """
    integer = 'int'
    float = 'float'
    boolean = 'boolean'
    string = 'java.lang.String'

    @staticmethod
    def from_dtype(dtype) -> DaikonType:
        """Interprets a Pandas/Numpy dtype as a DaikonType (where possible)"""
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
