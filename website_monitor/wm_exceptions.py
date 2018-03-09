# -*- coding: utf-8 -*-

"""Exceptions module."""


class ConfigFileEmpty(Exception):
    """The config file is empty."""
    pass


class ConfigFileInvalid(Exception):
    """The config file is not valid."""
    pass


class URLPropertyNotFound(Exception):
    """Website property does not specify required URL"""


class RequirementsNotFulfilled(Exception):
    """Content requirements were not matched for specific page response."""
    pass
