import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_profile(driver, link):
    print(f"Scraping profile: {link}")
    driver.get(link)
    time.sleep(2)  # Wait for the profile page to load

    try:
        name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "text-heading-xlarge"))
        ).text
        print(f"Name found: {name}")
    except:
        name = "N/A"
        print("Name not found")

    try:
        role = driver.find_element(By.CLASS_NAME, "text-body-medium").text
        print(f"Role found: {role}")
    except:
        role = "N/A"
        print("Role not found")

    contact_info = {}
    try:
        print("Attempting to click contact info button")
        contact_info_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[text()='Contact info']"))
        )
        contact_info_button.click()
        time.sleep(1)
        print("Contact info button clicked")

        # Extract email
        try:
            email = driver.find_element(By.XPATH, "//a[contains(@href, 'mailto:')]").text
            print(f"Email found: {email}")
        except:
            email = "N/A"
            print("Email not found")
        contact_info['email'] = email

        # Extract phone
        try:
            phone = driver.find_element(By.XPATH, "//h3[text()='Phone']/following-sibling::ul/li/span[1]").text
            print(f"Phone found: {phone}")
        except:
            phone = "N/A"
            print("Phone not found")
        contact_info['phone'] = phone

    except Exception as e:
        print(f"Error extracting contact info: {str(e)}")
        contact_info = {
            'email': "N/A",
            'phone': "N/A"
        }
        print("Using default N/A values for contact info")

    print("Profile scraping completed")
    return {
        "name": name,
        "role": role,
        "email": contact_info['email'],
        "phone": contact_info['phone'],
        "link": link
    }

def scrape_commenters(driver, url):
    driver.get(url)
    print(f"Navigated to {url}")

    # Wait for the page to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "comments-post-meta__profile-info-wrapper"))
    )
    print("Page loaded successfully")

    # Function to click "Load more comments" button
    def load_more_comments():
        try:
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "comments-comments-list__load-more-comments-button"))
            )
            driver.execute_script("arguments[0].click();", load_more_button)
            time.sleep(2)  # Wait for 2 seconds after clicking to avoid rate limits
            return True
        except:
            return False

    # Load all comments
    while load_more_comments():
        print("Loaded more comments")

    # Extract basic information
    name_elements = driver.find_elements(By.CLASS_NAME, "comments-post-meta__profile-info-wrapper")
    links = set()  # Use a set to store unique links
    for name_element in name_elements:
        link = name_element.find_element(By.TAG_NAME, "a").get_attribute("href")
        # Filter out company URLs
        if "/in/" in link:
            links.add(link)
    
    print(f"Found {len(links)} unique individual commenter profiles")
    return list(links)  # Convert set back to list before returning

def setup_driver(li_at):
    # Set up Chrome options
    chrome_options = Options()
    
    # Set up the WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the domain for which you want to set cookies
    driver.get("https://www.linkedin.com")
    print("Navigated to LinkedIn homepage")

    # Set cookies
    cookies = {
        'li_at': li_at,
    }

    for name, value in cookies.items():
        driver.add_cookie({'name': name, 'value': value})
    print("Cookies set")

    return driver