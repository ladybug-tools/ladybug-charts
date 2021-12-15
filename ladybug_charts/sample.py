import numpy as np
from ladybug.epw import EPW
from ladybug.analysisperiod import AnalysisPeriod
from ladybug.dt import DateTime
import random
import plotly.graph_objects as go
from .schema import mapping_dictionary, template, tight_margins
from math import ceil, floor


def heatmap(epw):

    month_tags = []
    for i in range(0, 24):
        ap = AnalysisPeriod(1, 1, i, 12, 31, i)
        moys = [DateTime.from_hoy(hoy).month for hoy in ap.hoys]
        month_tags.append(moys)

    data = epw.dry_bulb_temperature
    values = []
    for i in range(0, 24):
        item = data.filter_by_analysis_period(
            AnalysisPeriod(1, 1, i, 12, 31, i)).values
        values.append(item)

    hours = [str(h) for h in range(0, 24)]
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
              'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    # alt_days = [15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345]

    days = [str(d) for d in range(1, 366)]
    data = go.Heatmap(
        x=days,
        y=hours,
        z=values,
        zmin=data.min,
        zmax=data.max,
        customdata=month_tags,
        hovertemplate=(
            "<b>"
            + 'DBT'
            + ": %{z:.2f} "
            + 'C'
            + "</b><br>Month: %{customdata}<br>Day: %{x}<br>Hour: %{y}:00<br><extra></extra>"
        ))

    fig = go.Figure(data=data)

    fig.update_xaxes(dtick="M0.5", tickformat="%b", ticklabelmode="period")

    fig.update_yaxes(title_text="Hours of the day")
    fig.update_xaxes(title_text="Months of the year")

    fig.update_layout(template=template, margin=tight_margins,
                      yaxis_nticks=13)
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.show()
