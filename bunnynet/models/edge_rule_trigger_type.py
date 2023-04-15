import enum


class EdgeRuleTriggerType(enum.Enum):
    URL = 0
    REQUEST_HEADER = 1
    RESPONSE_HEADER = 2
    URL_EXTENSION = 3
    COUNTRY_CODE = 4
    REMOTE_IP = 5
    URL_QUERY_STRING = 6
    RANDOM_CHANCE = 7
