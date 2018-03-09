# -*- coding: utf-8 -*-

"""Main module."""
import copy
import datetime
import getopt
import json
import logging as log
import os
import re
import sys
import threading
import time

import requests

from website_monitor import db_utils
from .wm_exceptions import (
    ConfigFileEmpty, ConfigFileInvalid, RequirementsNotFulfilled,
    URLPropertyNotFound
)

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(WORK_DIR, 'logs')
LOG_FILE_PATH = os.path.join(LOG_DIR, 'logfile')

log.basicConfig(filename=LOG_FILE_PATH, format='%(message)s', level=log.INFO)


class Config(object):
    """Represents a configuration object."""

    def __init__(self, config_abs_path=None, check_period=0):
        """
        Initialize a Config instance.

        :param config_abs_path: String representing absolute path
            to configuration file
        :param check_period: Value representing the interval period between
            website status checks.
        """
        config_path = config_abs_path or os.path.join(WORK_DIR, 'config.json')
        configs = self._load_config(config_path)
        if check_period:
            # if check_period was set on CLI then it takes priority
            # over one specified in config file
            configs.pop('check_period', None)

        # sets default check_period to 3600s(1h) if not specified on CLI
        # nor in config file.
        self.check_period = check_period or configs.pop('check_period', 3600)
        self.websites = configs

    @property
    def check_period(self):
        return self.__check_period

    @check_period.setter
    def check_period(self, val):
        try:
            val = int(val)
        except ValueError:
            s = ('Please make sure that check period value is specified '
                 'as integer.')
            raise ValueError(s)

        if val < 0:
            s = ('Checking period cannot be negative. Please set correct '
                 'value and try again.')
            raise ValueError(s)
        self.__check_period = val

    @staticmethod
    def _validate_config(configs):
        """
        Class method used for validating config file.

        :param configs: dict containing configuration parameters
        :return: If successfully validated returns True,
            otherwise raises Exception
        """

        # check if config file is completely empty
        if not len(configs):
            s = ('The config file is empty. Please ensure that config file '
                 'is not empty and try again.')
            raise ConfigFileEmpty(s)

        # check if there are any other properties except 'check_period'
        tmp_data = copy.copy(configs)
        tmp_data.pop('check_period', 0)
        if not len(tmp_data):
            s = ('Please enter settings for at least one website in your '
                 'config file and try again.')
            raise ConfigFileInvalid(s)

        # check if website proprties have at least defined url
        for webname, web_data in configs.items():
            if webname == 'check_period':
                continue
            if 'url' not in web_data:
                s = ('Website property {} does not contain required URL '
                     'property. Please specify URL property and try again.')
                raise URLPropertyNotFound(s.format(webname))
        return True

    def _load_config(self, config_path):
        """
        Helper function used to read settings from configuration file.

        :return: If successfully read config file returns True
        """
        with open(config_path) as f:
            configs = json.load(f)

        self.__class__._validate_config(configs)

        return configs


class Monitor(object):
    """Represents Monitor object."""
    config_obj = None

    def __init__(self, config_obj):
        """
        Initialize a Monitor instance.

        :param config_obj: website_monitor.Config class instance
        """
        self.config = config_obj
        self.next_call = time.time()

    def start_watch(self):
        """
        Method responsible for triggering periodic checks in time intervals.
        If time interval is not specified it is set by default to 3600s(1h).

        :return: None
        """
        self._start_checks()
        self.next_call += self.config.check_period
        # accounts for drift
        # more at https://stackoverflow.com/a/18180189/2808371
        threading.Timer(self.next_call - time.time(), self.start_watch).start()

    def _start_checks(self):
        """
        Method responsible for coordinating checks of each website.

        :return: None
        """
        # used for formatting first and last message of round of checks
        time_format = '%d/%m/%Y %H:%M:%S'
        asterix = '*' * 10
        s = ('\n{asterix}Starting new round of checks - {current_time}'
             '{asterix}')
        log.info(s.format(asterix=asterix,
                          current_time=datetime.datetime.now().strftime(
                              time_format)))

        threads = []
        for webname, web_data in self.config.websites.items():
            url = web_data['url']
            content_requirements = web_data.get('content', None)
            t = threading.Thread(target=self._perform_checks, args=(
                url, content_requirements, webname))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        s = '\n{asterix}Finished all checks - {current_time}{asterix}'
        log.info(s.format(asterix=asterix,
                          current_time=datetime.datetime.now().strftime(
                              time_format)))

    def _perform_checks(self, url, content_requirements, webname):
        """
        Method responsible for checking requirements on each website.

        :param url: URL of the page for which we want to check requirements
        :param content_requirements: Actual content requirements
        :return: None
        """
        response = self.make_request(url, webname)

        if not response:
            return
        response_time = response.elapsed / datetime.timedelta(seconds=1)
        try:
            self.check_requirements(response, content_requirements)
        except RequirementsNotFulfilled as e:
            s = ('Content requirements: {e} ("{content_requirements}" '
                 'not in response content)')
            log.info(s.format(**locals()))
            db_utils.record_insert(webname, url, datetime.datetime.now(),
                                   response.status_code, response_time, 0)
        else:
            s = ('Content requirements: Website meets content requirements.'
                 '("{content_requirements}" in response content)')
            log.info(s.format(**locals()))
            db_utils.record_insert(webname, url, datetime.datetime.now(),
                                   response.status_code, response_time, 1)

    @staticmethod
    def make_request(url, webname=None):
        """
        Static method used to perform actual request to the server.

        :param url: URL of the page that we want to make request to
        :param webname: Alias name for website
        :return: If successful returns requests.Response object, otherwise None
        """
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            s = 'Connection problem\nError message: {}\n'
            log.info(s.format(error_msg))
            db_utils.record_insert(
                webname, url, request_time=datetime.datetime.now(),
                error=error_msg)
        else:
            s = ('\nURL: {url}\nStatus: {response.status_code}\n'
                 'Response time: {response.elapsed.seconds}s'
                 '{response.elapsed.microseconds}\u00B5s')
            log.info(s.format(**locals()))
            return response
        return None

    @staticmethod
    def check_requirements(response, content_requirements):
        """
        Static method used to perform requirement checks for specific
        requests.Response.

        :param response: requests.Response object.
        :param content_requirements: Content requirements to check against
            in response object.
        :return: If requirements are met returns True, otherwise raises
            website_monitor.exceptions.RequirementsNotFulfilled
        """
        response_content = response.content.decode('utf-8', 'ignore')
        requirements_are_met = re.search(content_requirements,
                                         response_content, re.IGNORECASE)

        if not content_requirements or requirements_are_met:
            # if there are no requirements or the requirements are fulfilled
            return True
        s = 'Website content does not match specified requirements.'
        raise RequirementsNotFulfilled(s.format(**locals()))


def parse_cl_args(argv):
    """
    Helper function used to check if user provided checking period value
    in command line arguments.

    :param argv: command line arguments
    :return: checking period value
    """
    help_text = """
    Usage:
        website_monitor.py -i <checking_interval_in_s>
        website_monitor.py --interval=<checking_interval_in_s>
    """
    try:
        opts, args = getopt.getopt(argv, "hi:", ["help", "interval="])
    except getopt.GetoptError:
        print(help_text)
        sys.exit(2)
    for opt, val in opts:
        if opt == '-h':
            print(help_text)
            sys.exit(0)
        elif opt in ("-i", "--interval"):
            return val

def main():
    interval = parse_cl_args(sys.argv[1:])
    db_utils.create_table()
    config = Config(check_period=interval)
    Monitor(config).start_watch()

if __name__ == '__main__':
    main()
