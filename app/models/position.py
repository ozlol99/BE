from enum import Enum


class PositionEnum(str, Enum):
    TOP = "top"
    JUNGLE = "jungle"
    MIDDLE = "mid"
    BOTTOM = "adc"
    SUPPORT = "sup"
    FILL = "FILL"
