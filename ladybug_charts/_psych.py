"""Recreating ladybug psychrometric chart using Plotly."""

import numpy as np
import pandas as pd

from math import ceil, floor

import plotly.io as pio
import plotly.graph_objects as go
from plotly.graph_objects import Figure

from ._helper import rgb_to_hex, mesh_to_coordinates

from ladybug.datacollection import BaseCollection
from ladybug import psychrometrics as psy
from ladybug.psychchart import PsychrometricChart
from ladybug_comfort.chart import polygonpmv
from ladybug_geometry.geometry2d.pointvector import Point2D

# set white background in all charts
pio.templates.default = 'plotly_white'


def _psych_chart(psych: PsychrometricChart, data: BaseCollection = None,
                 title: str = None) -> Figure:
    """Create a psychrometric chart.

    Args:
        psych: A ladybug PsychrometricChart object.
        data: A ladybug DataCollection object.
        title: A title for the plot. Defaults to None.

    Returns:
        A plotly figure.
    """

    dbt = psych.temperature
    rh = psych.relative_humidity
    hr = [psy.humid_ratio_from_db_rh(
        dbt.values[i], rh.values[i]) for i in range(len(dbt))]

    data_max = 5 * ceil(dbt.max / 5)
    data_min = 5 * floor(dbt.min / 5)
    var_range_x = [data_min, data_max]

    data_max = (5 * ceil(max(hr) * 1000 / 5)) / 1000
    data_min = (5 * floor(min(hr) * 1000 / 5)) / 1000
    var_range_y = [data_min, data_max]

    # create dummy psych-chart to create mesh
    base_point = Point2D(var_range_x[0], 0)
    psych_dummy = PsychrometricChart(dbt, rh, base_point=base_point, x_dim=1, y_dim=1)

    # prepare for drawing humidity lines
    dbt_list = list(range(-60, 60, 1))
    rh_list = list(range(10, 110, 10))

    rh_df = pd.DataFrame()
    for rh_item in rh_list:
        hr_list = np.vectorize(psy.humid_ratio_from_db_rh)(dbt_list, rh_item)
        name = "rh" + str(rh_item)
        rh_df[name] = hr_list

    fig = go.Figure()

    # Add curved lines for humidity
    for rh_item in rh_list:
        name = "rh" + str(rh_item)
        fig.add_trace(
            go.Scatter(
                x=dbt_list,
                y=rh_df[name],
                showlegend=False,
                mode="lines",
                name="",
                hovertemplate="RH " + str(rh_item) + "%",
                line=dict(width=1, color="#85837f"),
            )
        )

    if not data:
        title = 'Psychrometric Chart - Frequency'
        # Plot colored mesh
        cords = mesh_to_coordinates(psych_dummy.colored_mesh)
        for count, cord in enumerate(cords):
            fig.add_trace(
                go.Scatter(
                    x=cord[0],
                    y=cord[1],
                    fill='toself',
                    fillcolor=rgb_to_hex(psych.container.value_colors[count]),
                    line=dict(width=0),
                    showlegend=False,
                    mode='lines',
                )
            )

            # In plotly, it's not possible to have hover text on a filled shape
            # add another trace just to have hover text
            fig.add_trace(
                go.Scatter(
                    x=[psych_dummy.colored_mesh.face_centroids[count].x],
                    y=[psych_dummy.colored_mesh.face_centroids[count].y],
                    showlegend=False,
                    mode='markers',
                    opacity=0,
                    hovertemplate=str(int(psych_dummy.hour_values[count])) + ' hours' +
                    '<extra></extra>',
                )
            )

        # create a dummy trace to make the Legend
        colorbar_trace = go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            showlegend=False,
            marker=dict(
                colorscale=[rgb_to_hex(color)
                            for color in psych.legend_parameters.colors],
                showscale=True,
                cmin=psych.legend_parameters.min,
                cmax=psych.legend_parameters.max,
                colorbar=dict(thickness=30, title=psych.legend_parameters.title),
            ),
        )
        # add the dummy trace to the figure
        fig.add_trace(colorbar_trace)

    else:
        var = data.header.data_type.name
        var_unit = data.header.unit
        title = title if title else f'Psychrometric Chart - {var}'

        # add colored data mesh
        mesh, graphic_container = psych_dummy.data_mesh(data)
        cords = mesh_to_coordinates(mesh)
        for count, cord in enumerate(cords):
            fig.add_trace(
                go.Scatter(
                    x=cord[0],
                    y=cord[1],
                    fill='toself',
                    fillcolor=rgb_to_hex(graphic_container.value_colors[count]),
                    line=dict(width=0),
                    showlegend=False,
                    mode='lines'
                ))

            # In plotly, it's not possible to have hover text on a filled shape
            # add another trace just to have hover text
            fig.add_trace(
                go.Scatter(
                    x=[mesh.face_centroids[count].x],
                    y=[mesh.face_centroids[count].y],
                    showlegend=False,
                    mode='markers',
                    opacity=0,
                    hovertemplate=str(
                        int(graphic_container.values[count])) + ' '
                    + graphic_container.legend_parameters.title +
                    '<extra></extra>',
                )
            )

        # create a dummy trace to make the Legend
        colorbar_trace = go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            showlegend=False,
            marker=dict(
                colorscale=[rgb_to_hex(color)
                            for color in graphic_container.legend_parameters.colors],
                showscale=True,
                cmin=graphic_container.legend_parameters.min,
                cmax=graphic_container.legend_parameters.max,
                colorbar=dict(
                    thickness=30, title=graphic_container.legend_parameters.title),
            ),
        )

        # add the dummy trace to the figure
        fig.add_trace(colorbar_trace)

    fig.update_layout(
        template='plotly_white',
        margin=dict(l=20, r=20, t=33, b=20),
        title={
            'text': title,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        })

    fig.update_xaxes(
        title_text='Temperature (°C)',
        range=var_range_x,
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,
        dtick=5
    )
    fig.update_yaxes(
        title_text='Humidity Ratio (KG water/KG air)',
        range=var_range_y,
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,
    )
    return fig
