import enum


class TriggerMatchingType(enum.Enum):
    MATCH_ANY = 0
    MATCH_ALL = 1
    MATCH_NONE = 2
