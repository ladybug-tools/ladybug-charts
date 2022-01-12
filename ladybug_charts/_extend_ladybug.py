"""Add capability to generate a Figures from ladybug data objects. """

from plotly.graph_objects import Figure
from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyCollection, DailyCollection
from ladybug_charts.to_figure import heat_map, monthly_bar_chart, daily_bar_chart, \
    hourly_line_chart, per_hour_line_chart, wind_rose, psych_chart, bar_chart, sunpath
from ladybug.windrose import WindRose
from ladybug.psychchart import PsychrometricChart
from ladybug.hourlyplot import HourlyPlot
from ladybug.monthlychart import MonthlyChart
from ladybug.sunpath import Sunpath

HourlyContinuousCollection.heat_map = heat_map
HourlyDiscontinuousCollection.heat_map = heat_map
MonthlyCollection.bar_chart = monthly_bar_chart
DailyCollection.bar_chart = daily_bar_chart
HourlyContinuousCollection.line_chart = hourly_line_chart
HourlyContinuousCollection.per_hour_line_chart = per_hour_line_chart
WindRose.plot = wind_rose
PsychrometricChart.plot = psych_chart
Sunpath.plot = sunpath


def hourly_plot(self, title: str = None, show_title: bool = False) -> Figure:
    hourly_data = self.data_collection
    min_range = self.legend_parameters.min
    max_range = self.legend_parameters.max
    colors = self.legend_parameters.colors
    return heat_map(hourly_data, min_range, max_range, colors, title, show_title)


HourlyPlot.plot = hourly_plot


def plot_monthly_chart(self, min_range: float = None, max_range: float = None,
                       title: str = None, show_title: bool = False,
                       stack: bool = False) -> Figure:
    data = self.data_collections
    colors = self.colors
    return bar_chart(data, min_range, max_range, colors, title, show_title, stack)


MonthlyChart.plot = plot_monthly_chart
