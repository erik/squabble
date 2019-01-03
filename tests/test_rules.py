""" Odds and ends tests to hit corner cases etc in rules logic. """

import unittest

import pytest

import squabble.rule
from squabble import RuleConfigurationException, UnknownRuleException
from squabble.rules.add_column_disallow_constraints import \
    AddColumnDisallowConstraints


class TestDisallowConstraints(unittest.TestCase):

    def test_missing_constraints(self):
        with pytest.raises(RuleConfigurationException):
            AddColumnDisallowConstraints().enable(ctx={}, config={})

    def test_unknown_constraints(self):
        with pytest.raises(RuleConfigurationException):
            AddColumnDisallowConstraints().enable(ctx={}, config={
                'disallowed': ['UNIQUE', 'foo']
            })


class TestRuleRegistry(unittest.TestCase):
    def test_get_meta_unknown_name(self):
        with pytest.raises(UnknownRuleException):
            squabble.rule.Registry.get_meta('asdfg')

    def test_get_class_unknown_name(self):
        with pytest.raises(UnknownRuleException):
            squabble.rule.Registry.get_class('asdfg')
