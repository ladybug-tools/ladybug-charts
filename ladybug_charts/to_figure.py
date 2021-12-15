import numpy as np
import plotly.graph_objects as go
from pandas import DataFrame as Df
from plotly.graph_objects import Figure
from ._schema import mapping_dictionary, template, tight_margins
from .to_df import DataPoint
from math import ceil, floor


def heatmap(df: Df, var: DataPoint, global_local: str = "global") -> Figure:
    """Create a plotly heatmap figure.

    Args:
        df: A pandas dataframe.
        var: A string with the name of the variable to be plotted. Choose from one of the
        global_local: A string with the name of the global or local time.

    Returns:
        A plotly figure.
    """
    var = var.value
    var_unit = mapping_dictionary[var]["unit"]
    var_range = mapping_dictionary[var]["range"]
    var_color = mapping_dictionary[var]["color"]

    if global_local == "global":
        # Set Global values for Max and minimum
        range_z = var_range
    else:
        # Set maximum and minimum according to data
        data_max = 5 * ceil(df[var].max() / 5)
        data_min = 5 * floor(df[var].min() / 5)
        range_z = [data_min, data_max]

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
