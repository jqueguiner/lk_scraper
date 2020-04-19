from selenium import webdriver

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import random
import time
import re
import sys
import itertools

from lk_scraper.config.config import ScraperConfig


class Driver:
    def __init__(self, li_at_cookie=""):
        scraper_config = ScraperConfig()
        self.config = scraper_config.get_config()
        self.driver = self.build_driver()
        if self.driver:
            print("Driver loaded")
            if self.add_coookies(li_at_cookie=""):
                print("Cookies loaded")

    def build_driver(self):
        config = self.config['selenium']

        try:
            driver = webdriver.Remote(
                command_executor='%s://%s:%d/wd/hub' % (config['protocol'], config['host'], config['port']),
                desired_capabilities={'browserName': config['browserName'],
                                      'javascriptEnabled': config['javascriptEnabled']})
            self.driver = driver
            return driver

        except:
            print("Fail loading selenium driver")
            print("Make sure your selenium worker is deployed")
            print("For example you could launch a Selenium container")
            print("By typing: docker run -d -p4444:4444 --shm-size=2g selenium/standalone-firefox:3.141.59-20200326")
            print("Unexpected error:", sys.exc_info()[0])
            return False

    def add_coookies(self, li_at_cookie="") -> bool:
        config = self.config['linkedin']

        try:
            for cookie in config['cookies']:
                regex = r"([a-z].*\.[a-z].*)"
                self.driver.get("https://%s" % re.findall(regex, cookie['domain'])[0])
                self.driver.add_cookie({
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie['domain']
                })

            if not li_at_cookie == "":
                self.driver.add_cookie({
                    'name': 'li_at',
                    'value': li_at_cookie,
                    'domain': '.www.linkedin.com'
                })

            return True

        except:
            print("Fail loading cookies")
            return False

    def get(self, url):
        print(url)
        return self.driver.get(url)

    def browse(self, url) -> webdriver:
        self.driver.get(url)
        WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, "profile-nav-item")))

        for _ in itertools.repeat(None, 3):
            self.scroll_down()
            time.sleep(random.randrange(30, 100, 1) / 100)

    def get_page_source(self) -> str:
        source = self.driver.page_source
        return source

    def get_soup(self):
        source = self.get_page_source()
        soup = BeautifulSoup(source, 'html.parser')
        return soup

    def scroll_down(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_to_bottom(self, scroll_increment=300, timeout=10):
        """Scroll to the bottom of the page
        Params:
            - scroll_pause_time {float}: time to wait (s) between page scroll increments
            - scroll_increment {int}: increment size of page scrolls (pixels)
        """

        expandable_button_selectors = [
            'button[aria-expanded="false"].pv-skills-section__additional-skills',
            'button[aria-expanded="false"].pv-profile-section__see-more-inline',
            'button[aria-expanded="false"].pv-top-card-section__summary-toggle-button',
            'button[data-control-name="contact_see_more"]'
        ]

        current_height = 0

        while True:
            for name in expandable_button_selectors:
                try:
                    self.driver.find_element_by_css_selector(name).click()
                except:
                    pass

            # Use JQuery to click on invisible expandable 'see more...' elements
            self.driver.execute_script(
                'document.querySelectorAll(".lt-line-clamp__ellipsis:not(.lt-line-clamp__ellipsis--dummy) .lt-line-clamp__more").forEach(el => el.click())')

            # Scroll down to bottom
            new_height = self.driver.execute_script(
                "return Math.min({}, document.body.scrollHeight)".format(current_height + scroll_increment))
            if (new_height == current_height):
                break
            self.driver.execute_script(
                "window.scrollTo(0, Math.min({}, document.body.scrollHeight));".format(new_height))
            current_height = new_height
            # Wait to load page
            scroll_pause = random.randrange(0, 30, 1) / 1000
            time.sleep(scroll_pause)

    def click(self, xpath='//*[@id="ember419"]'):
        python_button = self.driver.find_elements_by_xpath(xpath)[0]
        python_button.click()
