"""Create plotly figures from pandas Dataframe."""


import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
from math import ceil, floor
from plotly.graph_objects import Figure
from typing import Union
from calendar import month_name
from random import randint

from ._to_dataframe import heatmap_dataframe
from ._helper import discontinuous_to_continuous, rgb_to_hex, ColorSet, color_set

from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyCollection, DailyCollection
from ladybug.color import Color
from ladybug_pandas.series import Series


def heatmap(hourly_data: Union[HourlyContinuousCollection, HourlyDiscontinuousCollection],
            min_range: float = None, max_range: float = None,
            colorset: ColorSet = ColorSet.original) -> Figure:
    """Create a plotly heatmap figure from Ladybug Hourly data.

    Args:
        hourly_data: A Ladybug HourlyContinuousCollection object or a Ladybug
            HourlyDiscontinuousCollection object.
        min_range: The minimum value for the legend of the heatmap. If not set, value
            will be calculated based on data. Defaults to None.
        max_range: The maximum value for the legend of the heatmap. If not set, value
            will be calculated based on data. Defaults to None.
        colorset: A ColorSets object. Defaults to Original Ladybug Colorset.

    Returns:
        A plotly figure.
    """
    assert isinstance(hourly_data, (HourlyContinuousCollection,
                      HourlyDiscontinuousCollection)), 'Only'
    ' Ladybug HourlyContinuousCollection and HourlyDiscontinuousCollection are supported.'
    f' Instead got {type(hourly_data)}'

    if isinstance(hourly_data, HourlyDiscontinuousCollection):
        hourly_data = discontinuous_to_continuous(hourly_data)

    var = hourly_data.header.data_type.name
    df = heatmap_dataframe()
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
            colorscale=[rgb_to_hex(color) for color in color_set[colorset.value]],
            customdata=np.stack((df["month_names"], df["day"]), axis=-1),
            hovertemplate=(
                "<b>"
                + var
                + ": %{z} "
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


def monthly_barchart(data: MonthlyCollection,
                     chart_title: str = 'Unnamed',
                     color: Color = Color(
                         randint(0, 255), randint(0, 255), randint(0, 255))
                     ) -> Figure:
    """Create a plotly barchart figure from Ladybug monthly data.

    Only continuous data is supported.

    Args:
        data: A Ladybug MonthlyCollection.
        chart_title: A string to be used as the title of the plot. Defaults to 'Unnamed'.
        color: A Ladybug color object. Defaults to a random color.

    Returns:
        A plotly figure.
    """
    assert isinstance(data, MonthlyCollection), 'Only continuous collections'\
        ' of monthly data is'\
        f' supported. Instead got {type(data)}'

    # name and unit
    var = data.header.data_type.name
    var_unit = data.header.unit

    fig_data = go.Bar(
        x=[month[:3] for month in month_name[1:]],
        y=[round(val, 2) for val in data.values],
        text=[f'{round(val, 2)} {var_unit}' for val in data.values],
        textposition='auto',
        hovertemplate='<br>%{y} ' + var_unit + '<br>' + '<extra></extra>',
        marker_color=rgb_to_hex(color)
    )

    fig = go.Figure(fig_data)
    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period")
    fig.update_yaxes(title_text=var + " (" + var_unit + ")")
    fig.update_xaxes(title_text="Months of the year")

    pio.templates.default = 'plotly_white'

    fig.update_layout(
        barmode='stack',
        template='plotly_white',
        margin=dict(l=20, r=20, t=33, b=20),
        yaxis_nticks=13,
        title={
            'text': chart_title,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

    return fig


def barchart(data: List[MonthlyCollection],
             chart_title: str = None,
             colors: List[Color] = None,
             stack: bool = False) -> Figure:
    """Create a plotly barchart figure from multiple ladybug monthly data objects.

    Args:
        data: A list of ladybug monthly data objects.
        chart_title: A string to be used as the title of the plot. If not set, the 
            names of data will be used to create a title for the chart. Defaults to None.
        colors: A list of ladybug color objects. The length of this list needs to match
            the length of data argument. If not set, random colors will be used.
            Defaults to None.
        stack: A boolean to determine whether to stack the data. Defaults to False which
            will show data side by side.

    Returns:
        A plotly figure.
    """
    assert len(data) > 0 and all([isinstance(item, MonthlyCollection) for item in data]), \
        f'Only a list of ladybug monthly data is supported. Instead got {type(data)}'

    if colors:
        assert len(colors) == len(data), 'Length of colors argument needs to match'\
            f' the length of data argument. Instead got {len(colors)} and {len(data)}'

    fig = go.Figure()
    names = []

    for count, item in enumerate(data):

        # find name unit and color
        var = item.header.data_type.name
        var_unit = item.header.unit
        color = colors[count] if colors else Color(
            randint(0, 255), randint(0, 255), randint(0, 255))

        fig_data = go.Bar(
            x=[month[:3] for month in month_name[1:]],
            y=[round(val, 2) for val in item.values],
            text=[f'{round(val, 2)} {var_unit}' for val in item.values],
            textposition='auto',
            hovertemplate='<br>%{y} ' + var_unit + '<br>' + '<extra></extra>',
            marker_color=rgb_to_hex(color),
            name=var
        )
        fig.add_trace(fig_data)
        names.append(var)

    # use chart title if set or join names
    chart_title = chart_title if chart_title else ' - '.join(names)

    fig.update_layout(
        barmode='relative' if stack else 'group',
        template='plotly_white',
        margin=dict(l=20, r=20, t=33, b=20),
        yaxis_nticks=13,
        title={
            'text': chart_title,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend={
            'x': 0,
            'y': 1.2,
        }
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

    return fig
