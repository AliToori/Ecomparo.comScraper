#!/usr/bin/env python3
"""
    *******************************************************************************************
    EcomparoScraper: Ecomparo Lead Scraper
    Author: Ali Toori, Full-Stack Python Developer
    Website: https://boteaz.com/
    *******************************************************************************************
"""
import json
import os
import re
import random
from time import sleep
import logging.config
import pandas as pd
import pyfiglet
import requests
from pathlib import Path
from multiprocessing import freeze_support
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service


class EcomparoScraper:
    def __init__(self):
        self.PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))
        self.file_settings = str(self.PROJECT_ROOT / 'BotRes/Settings.json')
        self.file_companies = self.PROJECT_ROOT / 'BotRes/Companies.csv'
        # self.proxies = self.get_proxies()
        self.user_agents = self.get_user_agents()
        self.settings = self.get_settings()
        self.LOGGER = self.get_logger()
        self.logged_in = False
        self.driver = None

    # Get self.LOGGER
    @staticmethod
    def get_logger():
        """
        Get logger file handler
        :return: LOGGER
        """
        logging.config.dictConfig({
            "version": 1,
            "disable_existing_loggers": False,
            'formatters': {
                'colored': {
                    '()': 'colorlog.ColoredFormatter',  # colored output
                    # --> %(log_color)s is very important, that's what colors the line
                    'format': '[%(asctime)s,%(lineno)s] %(log_color)s[%(message)s]',
                    'log_colors': {
                        'DEBUG': 'green',
                        'INFO': 'cyan',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'bold_red',
                    },
                },
                'simple': {
                    'format': '[%(asctime)s,%(lineno)s] [%(message)s]',
                },
            },
            "handlers": {
                "console": {
                    "class": "colorlog.StreamHandler",
                    "level": "INFO",
                    "formatter": "colored",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "simple",
                    "filename": "OpenSeaBot.log",
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 1
                },
            },
            "root": {"level": "INFO",
                     "handlers": ["console", "file"]
                     }
        })
        return logging.getLogger()

    @staticmethod
    def enable_cmd_colors():
        # Enables Windows New ANSI Support for Colored Printing on CMD
        from sys import platform
        if platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    @staticmethod
    def banner():
        pyfiglet.print_figlet(text='____________ EcomparoScraper\n', colors='RED')
        print('Author: AliToori, Full-Stack Python Developer\n'
              'Website: https://boteaz.com\n'
              '************************************************************************')

    def get_settings(self):
        """
        Creates default or loads existing settings file.
        :return: settings
        """
        if os.path.isfile(self.file_settings):
            with open(self.file_settings, 'r') as f:
                settings = json.load(f)
            return settings
        settings = {"Settings": {
            "ThreadsCount": 5
        }}
        with open(self.file_settings, 'w') as f:
            json.dump(settings, f, indent=4)
        with open(self.file_settings, 'r') as f:
            settings = json.load(f)
        return settings

    # Get random user agent
    def get_proxies(self):
        file_proxies = str(self.PROJECT_ROOT / 'BotRes/proxies.txt')
        with open(file_proxies) as f:
            content = f.readlines()
        return [x.strip() for x in content]

    # Get random user agent
    def get_user_agents(self):
        file_uagents = str(self.PROJECT_ROOT / 'BotRes/user_agents.txt')
        with open(file_uagents) as f:
            content = f.readlines()
        return [x.strip() for x in content]

    # Get web driver
    def get_driver(self, proxy=False, headless=False):
        driver_bin = str(self.PROJECT_ROOT / "BotRes/bin/chromedriver.exe")
        service = Service(executable_path=driver_bin)
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        prefs = {"directory_upgrade": True,
                 "credentials_enable_service": False,
                 "profile.password_manager_enabled": False,
                 "profile.default_content_settings.popups": False,
                 # "profile.managed_default_content_settings.images": 2,
                 "profile.default_content_setting_values.geolocation": 2,
                 "profile.managed_default_content_setting_values.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.add_argument(F'--user-agent={random.choice(self.user_agents)}')
        # if proxy:
            # options.add_argument(f"--proxy-server={random.choices(self.proxies)}")
        if headless:
            options.add_argument('--headless')
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    @staticmethod
    def wait_until_visible(driver, css_selector=None, element_id=None, name=None, class_name=None, tag_name=None, duration=10000, frequency=0.01):
        if css_selector:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
        elif element_id:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.ID, element_id)))
        elif name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.NAME, name)))
        elif class_name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
        elif tag_name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.TAG_NAME, tag_name)))

    def get_lead(self):
        driver = self.get_driver(headless=False)
        urls = {
            "Ecomparo_1": "https://www.ecomparo.de/shopsysteme-im-vergleich/",
            "Ecomparo_2": "https://www.ecomparo.de/e-commerce-warenwirtschaftssysteme-und-erp-loesungen-finden/?iCpv=2",
            "Ecomparo_3": "https://www.ecomparo.de/auswahl-von-all-in-one-e-commerce-loesungen-shopsysteme-und-erp/?iCpv=3",
                 }
        for url_name, url in urls.items():
            self.file_companies = self.PROJECT_ROOT / f'BotRes/{url_name}_Companies.csv'
            driver.get(url=url)
            self.wait_until_visible(driver=driver, css_selector='[name="AccordionMain"]')
            for section_index, section in enumerate(driver.find_elements(By.CSS_SELECTOR, '[name="AccordionMain"]')):
                section_name, description, text_info, company_name = '', '', '', ''
                section.click()
                self.wait_until_visible(driver=driver, css_selector='[class="acc-icon"]')
                section_name = section.find_element(By.CSS_SELECTOR, '[class="acc-icon"]').find_element(By.TAG_NAME, 'td').text
                description = section.find_element(By.CSS_SELECTOR, '[style="text-align:justify;"]').text
                for i, company in enumerate(section.find_elements(By.CSS_SELECTOR, '[name="criteriaItemName"]')):
                    self.LOGGER.info(f"Scraping Section: {section_index} | Company: {i}")
                    # Find company name directly from the main td element
                    company_name = company.text
                    # Reveal text info by clicking on the tooltip icon
                    try:
                        # Click on tooltip icon
                        company.find_element(By.CSS_SELECTOR, '[class="tooltip_search"]').click()
                        self.LOGGER.info(f"Waiting for text info to reveal")
                        # self.wait_until_visible(driver=company, css_selector='[class="tooltip_search_span"]')
                        text_info = company.find_element(By.CSS_SELECTOR, '[class="tooltip_search_span"]').text
                    except:
                        pass
                    data_dict = {"Section Name": section_name, "Description": description, "Company Name": company_name, "Text Information": text_info}
                    print(data_dict)
                    df = pd.DataFrame([data_dict])
                    # if file does not exist write headers
                    if not os.path.isfile(self.file_companies):
                        df.to_csv(self.file_companies, index=False)
                    else:  # else if exists, append without writing the headers
                        df.to_csv(self.file_companies, mode='a', header=False, index=False)
                    print(f'Leads saved successfully')

    def main(self):
        freeze_support()
        self.enable_cmd_colors()
        self.banner()
        self.LOGGER.info(f'EcomparoScraper launched')
        self.get_lead()


if __name__ == '__main__':
    EcomparoScraper().main()