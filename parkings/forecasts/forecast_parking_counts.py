import datetime

from catboost import CatBoostRegressor
from django.conf import settings

from parkings.forecasts.utils import (
    add_time_data_to_df, get_parking_area_parking_df, get_region_parking_df)
from parkings.models import ParkingArea, ParkingCount, Region

ITERATIONS = 200  # Optimized with grid search
LEARNING_RATE = 0.06  # Optimized with grid search
DEPTH = 8  # Optimized with grid search


def train_model(parking_df):
    """
    Train CatBoost model with parameters that were optimized in Google cloud with
    grid search.

    :param parking_df: Input dataset for the predictions.
    :type parking_df: pandas.DataFrame
    :return: The predicted signal name and the predictions as a vector.
    :rtype: str, numpy.ndarray
    """

    # Create separate CatBoost models for each column.
    for signal_name in parking_df.columns:
        training_parking_df = parking_df[[signal_name]]

        # Add input dataset for training data.
        shifted_df = training_parking_df.shift(settings.FORECAST_PERIOD)
        training_parking_df["shift_week_ago"] = shifted_df[[signal_name]]
        training_parking_df = training_parking_df.dropna()
        training_parking_df = add_time_data_to_df(training_parking_df)

        # Create prediction input dataset.
        prediction_df = shifted_df.tail(settings.FORECAST_PERIOD)
        prediction_df = prediction_df.rename(columns={signal_name: "shift_week_ago"})
        prediction_df = add_time_data_to_df(prediction_df)

        # Input signals.
        x_data = training_parking_df.drop(columns=[signal_name])
        # Expected output signal.
        y_data = training_parking_df[signal_name]

        model = CatBoostRegressor(
            iterations=ITERATIONS, learning_rate=LEARNING_RATE, depth=DEPTH
        )

        model.fit(x_data, y_data, verbose=False)

        predictions = model.predict(prediction_df)

        yield signal_name, predictions


def forecast_region_parking_counts():
    """
    Train model for Regions and get the predictions to save in the database.
    """
    parking_df = get_region_parking_df()
    # Datetime of the final entry in the input dataset.
    final_datetime = parking_df.index[-1].to_pydatetime()

    for signal_name, region_predictions in train_model(parking_df):
        region = Region.objects.get(name=signal_name)
        ParkingCount.objects.bulk_create(
            (
                ParkingCount(
                    is_forecast=True,
                    number=int(park_count),
                    region=region,
                    time=final_datetime + datetime.timedelta(hours=idx + 1),
                )
                for idx, park_count in enumerate(region_predictions)
            ),
            ignore_conflicts=True,
        )


def forecast_parking_area_parking_counts():
    """
    Train model for ParkingAreas and get the predictions to save in the database.
    """
    parking_df = get_parking_area_parking_df()
    # Datetime of the final entry in the input dataset.
    final_datetime = parking_df.index[-1].to_pydatetime()

    for signal_name, parking_area_predictions in train_model(parking_df):
        parking_area = ParkingArea.objects.get(origin_id=signal_name)
        ParkingCount.objects.bulk_create(
            (
                ParkingCount(
                    is_forecast=True,
                    number=int(park_count),
                    parking_area=parking_area,
                    time=final_datetime + datetime.timedelta(hours=idx + 1),
                )
                for idx, park_count in enumerate(parking_area_predictions)
            ),
            ignore_conflicts=True,
        )
