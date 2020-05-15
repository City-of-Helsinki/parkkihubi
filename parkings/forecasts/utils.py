import holidays
import pandas as pd
from django.conf import settings

from parkings.models import ParkingArea, ParkingCount, Region


def add_time_data_to_df(parking_df):
    """
    Adds holiday and time data to the DataFrame.

    :param parking_df: Original Pandas DataFrame.
    :type parking_df: pandas.DataFrame
    :return: Pandas DataFrame with the time data.
    :rtype: pandas.DataFrame
    """

    fi_holidays = holidays.CountryHoliday("FI")

    def is_holiday(ds):
        """
        Checks if the given datetime stamp is a Finnish holiday

        :param ds: Datetime stamp
        :type ds: datetime
        :return: 0 or 1 (boolean)
        :rtype: int
        """
        if ds in fi_holidays:
            return 1
        else:
            return 0

    parking_df["ds"] = parking_df.index
    parking_df["holiday"] = parking_df["ds"].apply(is_holiday)
    parking_df = parking_df.drop(columns=["ds"])

    parking_df["month"] = parking_df.index.month
    parking_df["day_of_week"] = parking_df.index.dayofweek
    parking_df["day_of_year"] = parking_df.index.dayofyear
    parking_df["hour"] = parking_df.index.hour

    return parking_df


def get_region_parking_df():
    """
    Help funciton to construct the DataFrame for Region parkings.

    :return: DataFrame of region parking data.
    :rtype: pandas.DataFrame, list, int
    """
    parking_dict = {}
    for region in Region.objects.all().order_by("name"):
        region_name = region.name
        parking_counts = (
            ParkingCount.objects.filter(
                is_forecast=False,
                region=region,
                time__gte=settings.FORECAST_PARKINGS_START,
            )
            .order_by("time")
            .values("number")
        )
        if not parking_counts:
            continue
        if region_name not in parking_dict:
            parking_dict[region_name] = []
        for parking_count in parking_counts:
            parking_dict[region_name].append(parking_count["number"])

    if not parking_dict:
        raise Exception("No cached ParkingCounts found.")

    start_time = (
        ParkingCount.objects.filter(
            region__isnull=False,
            is_forecast=False,
            time__gte=settings.FORECAST_PARKINGS_START,
        )
        .order_by("time")
        .first()
        .time
    )
    end_time = (
        ParkingCount.objects.filter(region__isnull=False, is_forecast=False)
        .order_by("time")
        .last()
        .time
    )
    dti = pd.date_range(start_time, end_time, freq="H")
    parking_df = pd.DataFrame(parking_dict, index=dti)
    parking_df = parking_df.tz_convert("Europe/Helsinki")

    # Clear regions with most frequent parking count being 0.
    columns_to_drop = []
    for region in parking_df.columns:
        if parking_df[region].value_counts().idxmax() == 0:
            columns_to_drop.append(region)
    parking_df = parking_df.drop(columns=columns_to_drop)

    # Remove extreme values.
    for region in parking_df.columns:
        hi = parking_df[[region]].quantile(0.999)[0]
        parking_df[region] = parking_df[region].clip(lower=1, upper=hi)

    return parking_df


def get_parking_area_parking_df():
    """
    Help funciton to construct the DataFrame for ParkingArea parkings.

    :return: DataFrame of parking area parking data.
    :rtype: pandas.DataFrame
    """
    parking_dict = {}
    for parking_area in ParkingArea.objects.all().order_by("origin_id"):
        parking_area_id = parking_area.origin_id
        parking_counts = (
            ParkingCount.objects.filter(
                is_forecast=False,
                parking_area=parking_area,
                time__gte=settings.FORECAST_PARKINGS_START,
            )
            .order_by("time")
            .values("number")
        )
        if not parking_counts:
            continue
        if parking_area_id not in parking_dict:
            parking_dict[parking_area_id] = []
        for parking_count in parking_counts:
            parking_dict[parking_area_id].append(parking_count["number"])

    if not parking_dict:
        raise Exception("No cached ParkingCounts found.")

    start_time = (
        ParkingCount.objects.filter(
            parking_area__isnull=False,
            is_forecast=False,
            time__gte=settings.FORECAST_PARKINGS_START,
        )
        .order_by("time")
        .first()
        .time
    )
    end_time = (
        ParkingCount.objects.filter(parking_area__isnull=False, is_forecast=False)
        .order_by("time")
        .last()
        .time
    )
    dti = pd.date_range(start_time, end_time, freq="H")
    parking_df = pd.DataFrame(parking_dict, index=dti)
    parking_df = parking_df.tz_convert("Europe/Helsinki")

    return parking_df
