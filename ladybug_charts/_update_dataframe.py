"""Functions to update the ladybug-pandas dataframe."""


import pandas as pd
from calendar import month_name


def update_dataframe_for_heatmap(data_frame) -> pd.DataFrame:
    """Add columns to the ladybug-pandas dataframe for heatmap."""

    # add years, month, day and hour columns
    data_frame.insert(loc=0, column="year", value=data_frame.index.year)
    data_frame.insert(loc=1, column="month", value=data_frame.index.month)
    data_frame.insert(loc=2, column="day", value=data_frame.index.day)
    data_frame.insert(loc=3, column="hour", value=data_frame.index.hour)

    # add month name column
    months_abbreviated = [month[:3] for month in month_name[1:]]
    month_number_name_dict = {count + 1: month for count,
                              month in enumerate(months_abbreviated)}
    data_frame.insert(loc=4, column="month_names", value=data_frame["month"].astype(
        'int').map(month_number_name_dict))

    # add UTC_time
    times = pd.date_range(
        "2019-01-01 00:00:00", "2020-01-01", closed="left", freq="H", tz="UTC"
    )
    data_frame['UTC_time'] = pd.to_datetime(times)

    return data_frame
