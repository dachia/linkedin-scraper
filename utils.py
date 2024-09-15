import time
import random
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def wait_random(wait_type='short'):
    wait_ranges = {
        'short': (0.5, 1.5),
        'standard': (1, 3),
        'long': (2, 5),
        'extra_long': (5, 10)
    }
    min_time, max_time = wait_ranges.get(wait_type, wait_ranges['standard'])
    time.sleep(random.uniform(min_time, max_time))

def navigate_to_url(driver, url, timeout=30):
    driver.get(url)
    try:
        # Wait for the page to load
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print(f"Successfully navigated to {url}")
    except TimeoutException:
        print(f"Timeout waiting for page to load: {url}")
    
    # Wait to avoid rate limits
    wait_random('standard')  # Changed from 'long' to 'standard'

def save_profiles_to_csv(profiles, filename='linkedin_profiles.csv'):
    fieldnames = ['name', 'role', 'email', 'phone', 'link']
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for profile in profiles:
            writer.writerow(profile)    
    print(f"Profiles saved to {filename}")
