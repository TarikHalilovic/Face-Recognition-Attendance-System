from enum import Enum

class Event(Enum):
    WORK_START = 1
    BREAK_START = 2
    OFFICIAL_START = 3
    WORK_END = 4
    BREAK_END = 5
    OFFICIAL_END = 6