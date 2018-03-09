#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `website_monitor` package."""

import pytest
import json

from website_monitor.website_monitor import Config, Monitor
from website_monitor.wm_exceptions import (
    ConfigFileEmpty, ConfigFileInvalid, RequirementsNotFulfilled,
    URLPropertyNotFound
)


class TestConfig(object):
    @pytest.fixture
    def config_path(self, tmpdir):
        return str(tmpdir / 'config_test.json')

    def test_initialization_with_default_values_works_correctly(self):
        config = Config()

        assert hasattr(config, 'check_period')
        assert hasattr(config, 'websites')

    def test_initialization_with_not_empty_config_file_initializes_instance_variables(
            self):
        config = Config()

        assert config.check_period > 0
        assert len(config.websites) > 0

    def test_initialization_with_empty_config_file_should_fail(
            self, config_path):
        with open(config_path, 'w') as f:
            json.dump({}, f)

        with pytest.raises(ConfigFileEmpty):
            Config(config_abs_path=config_path)

    def test_initialization_with_not_empty_config_file_without_website_properties_should_fail(
            self, config_path):
        with open(config_path, 'w') as f:
            json.dump({'check_period': 60}, f)

        with pytest.raises(ConfigFileInvalid):
            Config(config_abs_path=config_path)

    def test_initialization_with_not_empty_config_file_without_website_url_property_should_fail(
            self, config_path):
        with open(config_path, 'w') as f:
            json.dump({'google_index': {"content": "Search"}}, f)

        with pytest.raises(URLPropertyNotFound):
            Config(config_abs_path=config_path)

    def test_setting_check_period_value_to_negative_should_fail(self):
        with pytest.raises(ValueError):
            Config(check_period=-1)


class TestMonitor(object):
    url_valid = 'https://www.google.pl'
    url_invalid = 'https://oainsdobfuq2.com'

    @pytest.fixture
    def config(self):
        return Config()

    @pytest.fixture
    def monitor(self, config):
        return Monitor(config)

    @pytest.fixture
    def response_valid(self):
        return Monitor.make_request(self.__class__.url_valid)

    def test_make_request_with_valid_url_should_return_response_object(
            self, response_valid):
        response = response_valid
        assert response is not None

    def test_make_request_with_valid_url_should_return_200_status_code(
            self, response_valid):
        response = response_valid
        assert response.status_code == 200

    def test_make_request_with_invalid_url_should_return_none(self):
        response = Monitor.make_request(self.__class__.url_invalid)
        assert response is None

    def test_check_requirements_should_return_true_if_requirements_are_met(
            self, response_valid):
        response = response_valid
        meets_requirements = Monitor.check_requirements(response, 'google')
        assert meets_requirements is True

    def test_check_requirements_should_raise_exception_if_requirements_are_met(
            self, response_valid):
        response = response_valid
        with pytest.raises(RequirementsNotFulfilled):
            Monitor.check_requirements(response, 'thistextisnotonthepage')
