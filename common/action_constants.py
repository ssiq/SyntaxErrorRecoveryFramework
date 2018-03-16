from enum import Enum


class ActionType(Enum):
    NORMAL = 0
    INSERT_BEFORE = 1
    INSERT_AFTER = 2
    DELETE = 3
    CHANGE = 4
