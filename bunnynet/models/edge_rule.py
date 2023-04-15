import deserialize

from .edge_rule_action_type import EdgeRuleActionType
from .edge_rule_trigger import EdgeRuleTrigger
from .trigger_matching_type import TriggerMatchingType


@deserialize.auto_snake()
class EdgeRule:
    # The unique GUID of the edge rule
    guid: str

    # The action type of the edge rule.
    action_type: EdgeRuleActionType

    # The Action parameter 1. The value depends on other parameters of the edge rule.
    action_parameter_1: str | None

    # The Action parameter 2. The value depends on other parameters of the edge rule.
    action_parameter_2: str | None

    triggers: list[EdgeRuleTrigger]

    # The trigger matching type
    trigger_matching_type: TriggerMatchingType

    # The description of the edge rule
    description: str | None

    # Determines if the edge rule is currently enabled or not
    enabled: bool
