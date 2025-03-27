"""Defines Filter class and any behavior relevant to filtering results."""
from datetime import timedelta
from enum import StrEnum

from .utils import datetime_pst


class FilterEnum(StrEnum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    SEMIANNUAL = "semiannual"
    YEAR = "year"
    NONE = "none"

filter_td_map = {
    FilterEnum.DAY: timedelta(days=1),
    FilterEnum.WEEK: timedelta(weeks=1),
    FilterEnum.MONTH: timedelta(days=30),
    FilterEnum.QUARTER: timedelta(weeks=13),
    FilterEnum.SEMIANNUAL: timedelta(weeks=26),
    FilterEnum.YEAR: timedelta(days=365),
    FilterEnum.NONE: timedelta()
}

def parse_filter(member: FilterEnum) -> float:
    td = filter_td_map[member]
    if td.total_seconds() == 0:
        return 0
    else:
        return (datetime_pst.now() - td).timestamp()
