from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

import platform
import re
import os
import threading
import requests
import time

def windows_beep():
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 1000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
def apple_beep():
    AppKit.NSBeep()

_platform = platform.system()
if _platform == 'Windows':
    import winsound
    beep = windows_beep
elif _platform == 'Darwin':
    import AppKit
    beep = apple_beep



MINT_CODENAME = 'child_friendly'
TIMEOUT = 60 # seconds
REFRESH_EVERY = 32
NUMBER_TIMES_ALLOWED_UNSEEN = 100
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver_for_mac")
#DRIVER_BIN = os.path.join(PROJECT_ROOT, "bin/chromedriver.exe")
NUMBER_ATTEMPTS_TO_MAKE_API_CALL = 5
EVENT_ROW_CLASS_NAME = 'EventHistory--row'
EVENT_ICON_CLASS_NAME = 'EventHistory--icon'
DISPLAY_TICKS = True
OPENSEA_API_ASSET_URL = 'https://api.opensea.io/api/v1/asset'

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

def opensea_request_asset(asset_contact_address, token_id):
    url = '{0}/{1}/{2}'.format(OPENSEA_API_ASSET_URL, asset_contact_address, token_id)
    response = requests.request('GET', url)
    return response.json()

def opensea_profile_url(user):
    return 'https://opensea.io/{0}?tab=activity'.format(user)

def report_new_minted_asset(user, asset):
    beep()
    print('New child-friendly asset:')
    print('USER: {0}'.format(user))
    print('ASSET: {0}\n'.format(asset))

def handle_thread(driver, url):
    try:
        user = (re.findall('^https://opensea.io/(.*)\?.*$', url))[0]
    except IndexError:
        print('Bad URL format for ' + url + '\n')
        print('The format has to be: "https://opensea.io/USER_NAME?tab=activity".\n')
        
    known_minted = {}
    start_time = time.time()

    link = opensea_profile_url(user)
    print('##### ' + link +' ###\n')
    driver.get(link + '&search[eventTypes][0]=ASSET_TRANSFER')

    try:
        event_icon_present = EC.presence_of_element_located((By.CLASS_NAME, EVENT_ICON_CLASS_NAME))
        WebDriverWait(driver, TIMEOUT).until(event_icon_present)
    except TimeoutException:
        print('A timeout of {0} seconds has occurred on {1}\n'.format(TIMEOUT, link))
    
    initialize_mints(start_time, driver, user, known_minted)
    while True:
        new_minted = return_new_minted(driver, user, known_minted)
        for mint in new_minted:
            report_new_minted_asset(user, mint)
        if DISPLAY_TICKS and (not new_minted):
            print('---Ticked on {0}---\n'.format(user))
        time.sleep(REFRESH_EVERY - ((time.time() - start_time) % REFRESH_EVERY))

def initialize_mints(start_time, driver, user, known_minted):
    return_new_minted(driver, user, known_minted)
    time.sleep(REFRESH_EVERY - ((time.time() - start_time) % REFRESH_EVERY))

def return_new_minted(driver, user, known_minted):
    active_minted_seen = []
    new_minted = []
    for event in driver.find_elements_by_class_name(EVENT_ROW_CLASS_NAME):
        asset_icon_codename = event.find_element_by_class_name('EventHistory--icon').get_attribute('value')
        if (asset_icon_codename != MINT_CODENAME):
            continue
        try:
            asset_url = event.find_element_by_class_name('AssetCell--link').get_attribute('href')
            (asset_contact_address, token_id) = (re.findall("^.*\/assets\/(?:matic\/)?(0x[0-9a-z]+)\/(\d+)$", asset_url))[0]
            asset = '{0}/{1}'.format(asset_contact_address, token_id)
        except IndexError:
            print('Something is wrong with an asset on user "{0}".'.format(user))
            print('\Bad asset URL is {0}\n'.format(asset_url))
            continue
        
        if (not asset in known_minted):
            new_minted.append(asset)
        
        active_minted_seen.append(asset)
        known_minted[asset] = NUMBER_TIMES_ALLOWED_UNSEEN

    assets_to_remove = []
    for mint in known_minted:
        if (not mint in active_minted_seen):
            known_minted[mint] -= 1

            if (known_minted[mint] <= 0):
                assets_to_remove.append(mint)

    for asset in assets_to_remove:
        known_minted.pop(asset)

    return new_minted

def multi_threading(links):
    threads = {}
    for link in links:
        link_driver = webdriver.Chrome(executable_path = DRIVER_BIN, options = chrome_options)
        threads[link] = threading.Thread(target = handle_thread, args = (link_driver, link))
        threads[link].start()


links = (
    "https://opensea.io/0x2536c09e5f5691498805884fa37811be3b2bddb4?tab=activity",
    "https://opensea.io/0x12267aefd8bb461817df348ce16c933e76c1aa0d?tab=activity",
    "https://opensea.io/Helloitsme?tab=activity",
    "https://opensea.io/VashX?tab=activity",
    "https://opensea.io/BambooDerby?tab=activity",
    "https://opensea.io/0x90e5aa59a9df2add394df81521dbbed5f3c4a1a3?tab=activity",
    "https://opensea.io/emmya?tab=activity",
    "https://opensea.io/MBabs?tab=activity",
)
multi_threading(links)