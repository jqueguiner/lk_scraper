# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
# Copyright 2020 The lk_scraper Authors. All rights reserved.

import json
import os
import yaml

DEFAULT_SCRAPER_CONFIG_PATH = f'{os.environ["HOME"]}/.lk_scraper'
DEFAULT_SCRAPER_CONFIG_FILE = 'config.yml'
DEFAULT_SCRAPER_RULES_FILE = 'scraper_rules.json'


class ScraperConfig(object):
    """
    User specific scraper configuration object, read config file in the wanted directory
    """

    def __init__(self,
                 config_path: str = DEFAULT_SCRAPER_CONFIG_PATH,
                 config_file: str = DEFAULT_SCRAPER_CONFIG_FILE,
                 rules_file: str = DEFAULT_SCRAPER_RULES_FILE,
                 ):
        """
        Construct a ScraperConfig
        :param config_path: The path of the prescience configuration directory to use
        :param config_file: The name of the configuration file to use
        :param rules_file: The name of the rules file to use
        """
        self.config_path: str = config_path
        self.config_file: str = config_file
        self.rules_file: str = rules_file
        self.full_config_path: str = os.path.join(config_path, config_file)
        self.full_rules_path: str = os.path.join(config_path, rules_file)

        self.config = dict()
        self.selenium = dict()
        self.linkedin = dict()

        self.rules = dict()

        self.rules, self.config = self.load()

    def load(self) -> 'ScraperConfig':
        """
        Load the configuration depending on what's inside configuration file
        :return: self
        """
        ScraperConfig.create_config_path_if_not_exist(config_path=self.config_path)

        if os.path.isfile(self.full_config_path):
            print('Loading configuration file %s' % self.full_config_path)
            with open(self.full_config_path, 'r') as f:
                self.config = yaml.load(f, Loader=yaml.FullLoader)

            self.selenium = self.config['selenium']
            self.linkedin = self.config['linkedin']

            print('Loading rules file %s' % self.full_rules_path)
            with open(self.full_rules_path, 'r') as f:
                self.rules = json.load(f)

        return self.rules, self.config

    def get_rules(self) -> dict:
        return self.rules

    def get_selenium_config(self) -> dict:
        return self.selenium

    def get_linkedin_config(self) -> dict:
        return self.linkedin

    def get_config(self) -> dict():
        return self.config

    @staticmethod
    def create_config_path_if_not_exist(config_path: str = DEFAULT_SCRAPER_CONFIG_PATH) -> str:
        """
        Static method responsible for creating the configuration directory if it doesn't exist yet
        :param config_path: The configuration directory path to create if needed
        :return: The configuration directory path
        """
        if not os.path.exists(config_path):
            print(f'Directory \'{config_path}\' doesn\'t exists. Creating it...')
            os.makedirs(config_path)
        return config_path
