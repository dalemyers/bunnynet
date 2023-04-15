import deserialize

from .edge_rule_trigger_type import EdgeRuleTriggerType
from .pattern_matching_type import PatternMatchingType


@deserialize.key("trigger_type", "Type")
@deserialize.auto_snake()
class EdgeRuleTrigger:
    # The unique GUID of the edge rule
    trigger_type: EdgeRuleTriggerType

    # The list of pattern matches that will trigger the edge rule
    pattern_matches: list[str] | None

    # The type of pattern matching
    pattern_matching_type: PatternMatchingType

    # The trigger parameter 1. The value depends on the type of trigger.
    parameter_1: str | None
