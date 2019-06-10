from pandas import Series

from burdock.expander import Expander


class StatisticsExpander(Expander):
    def expand_constants(self, series: Series) -> Series:
        stats = series.describe()
        return stats.add_prefix(series.name + '_')


statistics_expander = StatisticsExpander(tag='type.numeric')
