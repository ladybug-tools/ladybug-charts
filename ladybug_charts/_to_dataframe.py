"""Functions to update the ladybug-pandas dataframe."""


import pandas as pd
from calendar import month_name
from enum import Enum

# Abbreviated month names
MONTHS = [month[:3] for month in month_name[1:]]


class Frequency(Enum):
    """Time interval of data."""

    HOURLY = "H"
    DAILY = "D"
    MONTHLY = "M"


def dataframe(frequency: Frequency = Frequency.HOURLY) -> pd.DataFrame:
    """Create a sample dataframe to be used in charts.

    Args:
        frequency: The frequency of the dataframe. Defaults to Hourly frequency.

    Returns
        A pandas dataframe.
    """

    data_frame = pd.DataFrame()
    
    
    # add time to create an index
    try:
        times = pd.date_range(
            "2019-01-01 00:00:00",
            "2020-01-01",
            closed="left",
            freq=frequency.value,
            tz="UTC"
        )
    except TypeError:
        times = pd.date_range(
            "2019-01-01 00:00:00",
            "2020-01-01",
            inclusive="left",
            freq=frequency.value,
            tz="UTC"
        )
    data_frame['times'] = times
    data_frame.set_index(
        "times", drop=False, append=False, inplace=True, verify_integrity=False)

    # add years, month, day and hour columns
    data_frame.insert(loc=0, column="year", value=data_frame.index.year)
    data_frame.insert(loc=1, column="month", value=data_frame.index.month)
    data_frame.insert(loc=2, column="day", value=data_frame.index.day)
    data_frame.insert(loc=3, column="hour", value=data_frame.index.hour)

    # add month name column
    month_number_name_dict = {count + 1: month for count,
                              month in enumerate(MONTHS)}
    data_frame.insert(loc=4, column="month_names", value=data_frame["month"].astype(
        'int').map(month_number_name_dict))

    data_frame['UTC_time'] = pd.to_datetime(times)

    return data_frame
