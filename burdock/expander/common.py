from pandas import Series, DataFrame

from burdock.expander import Expander


class StatisticsExpander(Expander):
    def expand_variables(self, series: Series) -> DataFrame:
        return super().expand_variables(series)

    def expand_constants(self, series: Series) -> DataFrame:
        return series \
            .describe() \
            .to_frame() \
            .transpose() \
            .add_prefix(series.name + '_') \



statistics_expander = StatisticsExpander(tag='type.numeric')
