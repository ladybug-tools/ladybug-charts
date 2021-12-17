import numpy as np
import plotly.graph_objects as go
from pandas import DataFrame as Df
from plotly.graph_objects import Figure
from ._schema import mapping_dictionary, template, tight_margins
from .to_dataframe import DataPoint
from math import ceil, floor


def heatmap(df: Df, var: DataPoint, min: float = None, max: float = None) -> Figure:
    """Create a plotly heatmap figure.

    Args:
        df: A pandas dataframe.
        var: A Datapoint object.
        min: The minimum value for the legend of the heatmap. Defaults to None.
        max: The maximum value for the legend of the heatmap. Defaults to None.

    Returns:
        A plotly figure.
    """
    var = var.value
    var_unit = mapping_dictionary[var]["unit"]
    var_color = mapping_dictionary[var]["color"]

    if min != None and max != None:
        range_z = [min, max]
    elif min != None and max == None:
        range_z = [min, 5 * ceil(df[var].max() / 5)]
    elif min == None and max != None:
        range_z = [5 * floor(df[var].min() / 5), max]
    else:
        # Set maximum and minimum according to data
        range_z = [5 * floor(df[var].min() / 5), 5 * ceil(df[var].max() / 5)]

    fig = go.Figure(
        data=go.Heatmap(
            y=df["hour"],
            x=df["UTC_time"].dt.date,
            z=df[var],
            colorscale=var_color,
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

    fig.update_layout(template=template, margin=tight_margins, yaxis_nticks=13)
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

    return fig
