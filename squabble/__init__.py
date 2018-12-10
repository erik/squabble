import logging


logging.basicConfig()
logger = logging.getLogger(__name__)


class SquabbleException(Exception):
    """Base exception type for all things in this package"""
