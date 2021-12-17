"""Create plotly figures from pandas Dataframe."""

import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from ._to_dataframe import heatmap_dataframe
from math import ceil, floor
from ladybug.datacollection import HourlyContinuousCollection
from ladybug_pandas.series import Series


def heatmap(hourly_data: HourlyContinuousCollection,
            min_range: float = None, max_range: float = None) -> Figure:
    """Create a plotly heatmap figure from Ladybug HourlyContinuousCollection.

    Args:
        hourly_data: A Ladybug HourlyContinuousCollection object.
        min_range: The minimum value for the legend of the heatmap. If not set, value
            will be calculated based on data. Defaults to None.
        max_range: The maximum value for the legend of the heatmap. If not set, value
            will be calculated based on data. Defaults to None.

    Returns:
        A plotly figure.
    """
    df = heatmap_dataframe()
    var = hourly_data.header.data_type.name
    series = Series(hourly_data)
    df[var] = series.values
    var_unit = df[var].dtype.name.split('(')[-1].split(')')[0]

    if min_range != None and max_range != None:
        range_z = [min_range, max_range]
    elif min_range != None and max_range == None:
        range_z = [min_range, 5 * ceil(df[var].max() / 5)]
    elif min_range == None and max_range != None:
        range_z = [5 * floor(df[var].min() / 5), max_range]
    else:
        # Set maximum and minimum according to data
        range_z = [5 * floor(df[var].min() / 5), 5 * ceil(df[var].max() / 5)]

    fig = go.Figure(
        data=go.Heatmap(
            y=df["hour"],
            x=df["UTC_time"].dt.date,
            z=df[var],
            zmin=range_z[0],
            zmax=range_z[1],
            customdata=np.stack((df["month_names"], df["day"]), axis=-1),
            hovertemplate=(
                "<b>"
                + var
                + ": %{z:.2f} "
                + var_unit
                + "</b><br>Month: %{customdata[0]}<br>Day: %{customdata[1]}<br>Hour: %{y}:00<br>"
            ),
            name="",
            colorbar=dict(title=var_unit),
        )
    )

    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period")

    fig.update_yaxes(title_text="Hours of the day")
    fig.update_xaxes(title_text="Days of the year")

    pio.templates.default = 'plotly_white'
    fig.update_layout(template='plotly_white', margin=dict(
        l=20, r=20, t=33, b=20), yaxis_nticks=13)
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

    return fig
