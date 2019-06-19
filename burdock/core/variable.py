from typing import Optional, Dict

from pandas import DataFrame, Series

from burdock.core.type import DaikonType


class DaikonVariable:
    def __init__(self, name: str, rep_type: DaikonType, dec_type: Optional[str] = None, constant_value=None):
        self.name = name
        self.var_kind = 'variable'
        self.rep_type = rep_type
        self.dec_type = dec_type if dec_type else rep_type.name
        self.comparability = None
        self.constant_value = constant_value

    @property
    def is_integer(self) -> bool:
        return self.rep_type == DaikonType.integer

    @property
    def is_float(self) -> bool:
        return self.rep_type == DaikonType.float

    @property
    def is_boolean(self) -> bool:
        return self.rep_type == DaikonType.boolean

    @property
    def is_string(self) -> bool:
        return self.rep_type == DaikonType.string

    @property
    def is_constant(self) -> bool:
        return self.constant_value is not None

    def __str__(self):
        if self.is_constant:
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


def consts_from_df(df: DataFrame) -> Dict[str, DaikonVariable]:
    return {
        name: DaikonVariable(name, DaikonType.from_dtype(dtype), constant_value=df[name].iloc[0])
        for name, dtype
        in df.dtypes.iteritems()
    }


def vars_from_df(df: DataFrame) -> Dict[str, DaikonVariable]:
    return {
        name: DaikonVariable(name, DaikonType.from_dtype(dtype))
        for name, dtype
        in df.dtypes.iteritems()
    }
