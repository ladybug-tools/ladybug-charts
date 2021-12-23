"""Add capability to generate a Figures from ladybug data objects. """

from ladybug.datacollection import HourlyContinuousCollection, HourlyDiscontinuousCollection, MonthlyCollection
from ladybug_charts.to_figure import heatmap, monthly_bar_chart


HourlyContinuousCollection.heatmap = heatmap
HourlyDiscontinuousCollection.heatmap = heatmap
MonthlyCollection.barchart = monthly_bar_chart
