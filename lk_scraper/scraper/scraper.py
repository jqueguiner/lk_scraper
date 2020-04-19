import hashlib

from selenium import webdriver

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import re
import json

from lk_scraper.scraper.driver import Driver
from lk_scraper.config.config import ScraperConfig


class Scraper:
    def __init__(self, li_at=""):
        scraper_config = ScraperConfig()

        self.rules = scraper_config.get_rules()
        self.config = scraper_config.get_config()
        self.driver = Driver(li_at)

    def extract_field(self, data, field='name') -> dict():
        out = ""

        dateFields = ['dateRange', 'birthDateOn']

        if any(dateField in field for dateField in dateFields):
            out = {}
            try:
                out[field] = data[field]
            except:
                pass

            try:
                del out[field]['end']['$type']
            except:
                pass

            try:
                del out[field]['start']['$type']
            except:
                pass

        elif 'Urn' in field:
            try:
                out[field] = hashlib.sha1(data[field].encode())
            except:
                pass
        else:
            try:
                out = data[field]
            except:
                pass

        try:
            del out[field]['$type']
        except:
            pass

        if isinstance(out, dict):
            for k in list(out):
                if isinstance(out[k], dict):
                    for l in list(out[k]):
                        if k == '$type':
                            del out[k][l]

                else:
                    if k == '$type':
                        del out[k]
        return out

    def extract_from_json(self, soup, fields_to_extract):
        out = dict()

        code_snippets = soup.findAll("code")

        for output_dict_key, extract in fields_to_extract.items():
            output_dict_key = output_dict_key.rsplit('.', 1)[1]
            out[output_dict_key] = list()

        for code in code_snippets:
            if 'com.linkedin.voyager' in code.text.strip():
                data = json.loads(code.text.strip())

                if 'included' in data:
                    data = data['included']

                    for rule_key, rule in fields_to_extract.items():
                        for sub_dataset in data:
                            if '$type' in sub_dataset:

                                if sub_dataset['$type'] == rule_key:
                                    temp = dict()

                                    for field in rule['fields']:
                                        if field in sub_dataset:
                                            temp[field] = sub_dataset[field]

                                    if 'custom_fields' in rule:
                                        for k, field in rule['custom_fields'].items():
                                            try:
                                                temp[k] = re.search(field['regex'], temp[field['field']],
                                                                    re.IGNORECASE).group(1)
                                            except:
                                                pass

                                    if rule['list']:
                                        out[rule_key.rsplit('.', 1)[1]].append(temp)
                                    else:
                                        out[rule_key.rsplit('.', 1)[1]] = temp

                            if '$recipeTypes' in sub_dataset:

                                for rtype in sub_dataset['$recipeTypes']:

                                    if rtype == rule_key:
                                        temp = dict()
                                        for field in rule['fields']:
                                            if field in sub_dataset:
                                                temp[field] = sub_dataset[field]

                                        if 'custom_fields' in rule:
                                            for k, field in rule['custom_fields'].items():
                                                try:
                                                    temp[k] = re.search(field['regex'], temp[field['field']],
                                                                        re.IGNORECASE).group(1)
                                                except:
                                                    pass

                                        if rule['list']:
                                            out[rule_key.rsplit('.', 1)[1]].append(temp)
                                        else:
                                            out[rule_key.rsplit('.', 1)[1]] = temp

        return out

    def get_driver(self) -> webdriver:
        return self.driver

    def get_config(self) -> dict:
        return self.config

    def get_rules(self) -> dict:
        return self.rules

    def extract_object(self, url, rules):
        try:
            print("scraping : %s" % url)
            self.driver.browse(url=url)
        except:
            self.driver = Driver()
            self.driver.browse(url=url)

        soup = self.driver.get_soup()
        return self.extract_from_json(soup, rules)

    def get_object(self, object_name='company', object_id='apple', full_url=""):

        object_rules = self.rules[object_name]

        if not full_url == "":
            url = full_url
        else:
            url_placeholder = object_rules['url_placeholder']
            url = url_placeholder % str(object_id)

        lk_object = self.extract_object(url, object_rules['extract_rules'])

        if 'subsections' in object_rules:
            for key, subsection in object_rules['subsections'].items():
                regex = r"{(.*)}"
                url = subsection['url_placeholder']

                for match in re.findall(regex, url):
                    replacement = lk_object
                    keys = match.split(".")

                    for index in keys:
                        try:
                            index = int(index)
                        except:
                            pass

                        replacement = replacement[index]

                    url = url.replace('{%s}' % match, replacement)

                subsection_dict = list()

                if "crawler" in subsection:
                    for page_index in range(1, subsection['crawler']['limit']):
                        url = url + subsection['crawler']['prefix'] + str(page_index)
                        subsection_object = self.extract_object(url, subsection['extract_rules'])
                        subsection_dict.append(subsection_object)
                else:
                    subsection_dict = self.extract_object(url, subsection['extract_rules'])

                lk_object[key] = subsection_dict

        return lk_object
