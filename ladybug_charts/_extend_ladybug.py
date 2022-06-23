"""Add capability to generate a Figures from ladybug data objects. """

from typing import List
from plotly.graph_objects import Figure
from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyCollection, DailyCollection
from ladybug_charts.to_figure import heat_map, monthly_bar_chart, daily_bar_chart, \
    hourly_line_chart, diurnal_average_chart_from_hourly, wind_rose, psych_chart, \
    bar_chart, sunpath, diurnal_average_chart
from ladybug.windrose import WindRose
from ladybug.psychchart import PsychrometricChart
from ladybug.hourlyplot import HourlyPlot
from ladybug.monthlychart import MonthlyChart
from ladybug.sunpath import Sunpath
from ladybug.epw import EPW

HourlyContinuousCollection.heat_map = heat_map
HourlyDiscontinuousCollection.heat_map = heat_map
MonthlyCollection.bar_chart = monthly_bar_chart
DailyCollection.bar_chart = daily_bar_chart
HourlyContinuousCollection.line_chart = hourly_line_chart
HourlyContinuousCollection.diurnal_average_chart = diurnal_average_chart_from_hourly
WindRose.plot = wind_rose
PsychrometricChart.plot = psych_chart
Sunpath.plot = sunpath
EPW.diurnal_average_chart = diurnal_average_chart


def hourly_plot(self, title: str = None, show_title: bool = False,
                num_labels: int = None, labels: List[float] = None) -> Figure:
    hourly_data = self.data_collection
    min_range = self.legend_parameters.min
    max_range = self.legend_parameters.max
    colors = self.legend_parameters.colors
    return heat_map(hourly_data, min_range, max_range, colors, title, show_title,
                    num_labels, labels)


HourlyPlot.plot = hourly_plot


def plot_monthly_chart(self, min_range: float = None, max_range: float = None,
                       title: str = None, center_title: bool = False) -> Figure:
    assert isinstance(self.data_collections[0], (MonthlyCollection, DailyCollection)), \
        'MonthlyChart data collections must be Monthly or Daily to use plot().'
    data = self.data_collections
    colors = self.colors
    stack = self.stack
    return bar_chart(data, min_range, max_range, colors, title, center_title, stack)


MonthlyChart.plot = plot_monthly_chart
