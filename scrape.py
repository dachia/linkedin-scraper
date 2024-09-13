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
        links.add(link)
    
    print(f"Found {len(links)} unique commenter profiles")
    return list(links)  # Convert set back to list before returning

def setup_driver():
    # Set up Chrome options
    chrome_options = Options()
    
    # Set up the WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the domain for which you want to set cookies
    driver.get("https://www.linkedin.com")
    print("Navigated to LinkedIn homepage")

    # Set cookies
    cookies = {
        'li_at': 'AQEDAQkg7CwEdF8OAAABkez3lokAAAGSEQQaiU4AZzFN_Jbi2Jqo7otc2EM-hwf6NuPUJj3MVfn1mH9IvrKA3amCsdC7djaGohRuHPG6IetpcWc9jVFOhM9aXMwey4_1iCATTpfxgatQFc2-lYxX09v3',
    }

    for name, value in cookies.items():
        driver.add_cookie({'name': name, 'value': value})
    print("Cookies set")

    return driver

def save_profiles_to_csv(profiles, filename='linkedin_profiles.csv'):
    fieldnames = ['name', 'role', 'email', 'phone', 'link']
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for profile in profiles:
            writer.writerow(profile)
    
    print(f"Profiles saved to {filename}")

def linkedin_scraper(url):
    driver = setup_driver()

    try:
        # Scrape commenters
        commenter_links = scrape_commenters(driver, url)
        
        profiles = []
        for i, link in enumerate(commenter_links, 1):
            print(f"Processing profile {i}/{len(commenter_links)}: {link}")
            profile = scrape_profile(driver, link)
            profiles.append(profile)
            time.sleep(2)  # Wait before processing the next profile to avoid rate limits

        # Save profiles to CSV
        save_profiles_to_csv(profiles)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Current page source:")
        print(driver.page_source)

    finally:
        # Close the browser
        driver.quit()

# Example usage
linkedin_url = "https://www.linkedin.com/posts/gisenberg_i-just-uploaded-a-new-podcast-with-jason-activity-7238939519310331905-HrIa"
linkedin_scraper(linkedin_url)