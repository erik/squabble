import logging


logger = logging.getLogger(__name__)


class SquabbleException(Exception):
    """Base exception type for all things in this package"""


class RuleConfigurationException(SquabbleException):
    def __init__(self, rule, msg):
        self.rule = rule
        self.msg = msg


class UnknownRuleException(SquabbleException):
    def __init__(self, name):
        super().__init__('unknown rule: "%s"' % name)
