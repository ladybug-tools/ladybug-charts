"""Add capability to generate a Figures from ladybug data objects. """

from ladybug.datacollection import HourlyContinuousCollection
from ladybug_charts.to_figure import heatmap


HourlyContinuousCollection.heatmap = heatmap
