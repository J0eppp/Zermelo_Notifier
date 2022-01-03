import datetime


def millis_to_datetime(millis) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(
        millis / 1000.0, tz=datetime.timezone.utc)
