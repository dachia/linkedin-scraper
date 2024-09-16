import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import math
from utils import (
    wait_random, navigate_to_url, setup_driver, human_like_mouse_move,
    get_header_height, is_element_in_viewport, human_like_scroll, human_like_click,
    close_modal, human_like_scroll_page, hide_chat, accept_cookies
)

def scrape_profile(driver, link):
    print(f"Scraping profile: {link}")
    navigate_to_url(driver, link)
    wait_random()

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
        human_like_click(driver, contact_info_button)
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

    wait_random('short')
    print("Profile scraping completed")
    return {
        "name": name,
        "role": role,
        "email": contact_info['email'],
        "phone": contact_info['phone'],
        "link": link
    }

def scrape_commenters(driver, url):
    navigate_to_url(driver, url)
    print(f"Navigated to {url}")
    wait_random()

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
            human_like_scroll(driver, load_more_button)
            human_like_click(driver, load_more_button)
            wait_random()
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
    wait_random()
    return list(links)  # Convert set back to list before returning

def auto_connect(driver, url, max_pages=10):
    print("Starting auto-connect process")
    navigate_to_url(driver, url)
    print(f"Navigated to {url}")
    wait_random()

    pages_processed = 0

    while pages_processed < max_pages:
        human_like_scroll_page(driver)  # Scroll to load elements
        
        connect_buttons = driver.find_elements(By.XPATH, "//button[.//span[text()='Connect']]")
        print(f"Found {len(connect_buttons)} connect buttons on the page")
        
        if not connect_buttons:
            print("No more connect buttons found on this page")
            break

        for button in connect_buttons:
            try:
                human_like_scroll(driver, button)
                wait_random('short')
                
                clickable_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[@id='{button.get_attribute('id')}']"))
                )
                
                human_like_click(driver, clickable_button)
                print("Clicked Connect button")
                
                wait_random()
                send_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Send without a note']"))
                )
                
                if 'artdeco-button--disabled' in send_button.get_attribute('class'):
                    print("Send button is disabled. Closing the modal.")
                    close_modal(driver)
                    continue
                
                human_like_click(driver, send_button)
                print("Sent connection request")
                
                wait_random()
            except Exception as e:
                print(f"Error connecting: {str(e)}")
                print("Attempting to recover...")
                close_modal(driver)
                remaining_buttons = driver.find_elements(By.XPATH, "//button[.//span[text()='Connect']]")
                if not remaining_buttons:
                    print("No more connect buttons available after error recovery. Moving to next page.")
                    break
                continue
        
        try:
            print("Looking for next button")
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'artdeco-pagination__button--next')]"))
            )
            print("Next button found")
            human_like_scroll(driver, next_button)
            
            if next_button.is_enabled() and next_button.is_displayed():
                human_like_click(driver, next_button)
                print("Clicked Next button")
                pages_processed += 1
                wait_random()
            else:
                print("Next button found but not clickable. Ending auto-connect process.")
                break
        except Exception as e:
            print(f"Error finding or clicking Next button: {str(e)}")
            print("No Next button found or error occurred. Ending auto-connect process.")
            break

def configure_filters(driver, url, current_company=None, past_company=None, locations=None, connections=None, current_role=None):
    print("Starting filter configuration")
    navigate_to_url(driver, url)
    print(f"Navigated to URL: {url}")
    accept_cookies(driver)
    # hide_chat(driver)

    # Click on "All filters" button to open filters
    all_filters_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'search-reusables__all-filters-pill-button') and @aria-label='Show all filters. Clicking this button displays all available filter options.']"))
    )
    print("Clicking on 'All filters' button")
    human_like_click(driver, all_filters_button)
    
    # Wait for the filters to be expanded
    print("Waiting for filters to expand")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[@aria-expanded='true' and contains(@class, 'search-reusables__all-filters-pill-button')]"))
    )
    print("Filters expanded successfully")

    # Wait for the filter modal to appear
    print("Waiting for filter modal to appear")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "search-reusables__side-panel"))
    )
    print("Filter modal is now visible")

    # Set current company
    if current_company:
        print(f"Setting current company filters: {current_company}")
        for company in current_company:
            set_company_filter(driver, "current-company-filter-value", company)
            # wait_random()
    
    
    # Click "Show results" button
    print("Clicking 'Show results' button")
    show_results_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'search-reusables__secondary-filters-show-results-button')]"))
    )
    human_like_click(driver, show_results_button)
    
    # Wait for results to load
    print("Waiting for results to load")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "search-results-container"))
    )
    print("Results loaded successfully")

def set_company_filter(driver, filter_name, company):
    print(f"Setting company filter: {filter_name} = {company}")
    try:
        # Locate the filter modal content div
        filter_modal_content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "artdeco-modal__content"))
        )

        # Scroll to the "Add a company" button within the filter modal
        add_company_button = WebDriverWait(filter_modal_content, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'reusable-search-filters-advanced-filters__add-filter-button') and .//span[text()='Add a company']]"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_company_button)
        print("Scrolled to center 'Add a company' button")

        human_like_click(driver, add_company_button)
        print("Clicked 'Add a company' button")
        
        company_search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Add a company']"))
        )
        print(f"Found company search input")
        company_search.send_keys(company)
        print(f"Entered company name: {company}")
        
        wait_random('short')
        
        # Implement retry mechanism for company selection
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                company_option = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'basic-typeahead__selectable')][1]"))
                )
                print(f"Found company option: {company}")
                company_option.click()
                # human_like_click(driver, company_option)
                print(f"Clicked company option: {company}")
                break  # If successful, exit the retry loop
            except StaleElementReferenceException:
                if attempt < max_attempts - 1:
                    print(f"Stale element when selecting company. Retrying... (Attempt {attempt + 1}/{max_attempts})")
                    wait_random('short')  # Wait before retrying
                else:
                    print(f"Failed to select company after {max_attempts} attempts.")
                    raise
            except TimeoutException:
                print(f"Timeout while waiting for company option. Retrying... (Attempt {attempt + 1}/{max_attempts})")
                if attempt == max_attempts - 1:
                    raise

        print(f"Successfully set company filter: {filter_name} = {company}")
    except Exception as e:
        print(f"Error in set_company_filter: {str(e)}")
        raise

def scrape_search(driver, url):
    driver.get(url)
    wait_random()
    
    profile_links = []
    profiles = []  # List to store profile details
    
    # Find all profile link elements
    link_elements = driver.find_elements(By.CSS_SELECTOR, "div.entity-result__divider")
    
    # Extract href attributes and other details
    for index, element in enumerate(link_elements, 1):
        print(f"Processing element {index}/{len(link_elements)}")
        
        try:
            link_element = element.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a.app-aware-link")
            link = link_element.get_attribute("href")
            name_element = link_element.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
            name = name_element.text.strip()
            print(f"Found link: {link}")
            print(f"Found name: {name}")
        except Exception as e:
            continue
            print(f"Error finding link: {str(e)}")
            link = "N/A"
        
        try:
            role = element.find_element(By.CSS_SELECTOR, "div.entity-result__primary-subtitle").text
            print(f"Found role: {role}")
        except Exception as e:
            print(f"Error finding role: {str(e)}")
            role = "N/A"
        
        try:
            location = element.find_element(By.CSS_SELECTOR, "div.entity-result__secondary-subtitle").text
            print(f"Found location: {location}")
        except Exception as e:
            print(f"Error finding location: {str(e)}")
            location = "N/A"
        
        profile_links.append(link)
        profiles.append({
            "name": name,
            "role": role,
            "location": location,
            "link": link
        })
    
    # Scrape 20 pages
    for page in range(1, 21):
        print(f"Scraping page {page}")
        
        # Human-like scroll through the page
        wait_random('standard')
        
        # Find all profile link elements again after scrolling
        link_elements = driver.find_elements(By.CSS_SELECTOR, "div.entity-result__divider")
        
        # Extract href attributes and other details
        for index, element in enumerate(link_elements, 1):
            print(f"Processing element {index}/{len(link_elements)}")
            
            try:
                link_element = element.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a.app-aware-link")
                link = link_element.get_attribute("href")
                name_element = link_element.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
                name = name_element.text.strip()
                print(f"Found link: {link}")
                print(f"Found name: {name}")
            except Exception as e:
                print(f"Error finding link: {str(e)}")
                continue
            
            try:
                role = element.find_element(By.CSS_SELECTOR, "div.entity-result__primary-subtitle").text
                print(f"Found role: {role}")
            except Exception as e:
                print(f"Error finding role: {str(e)}")
                role = "N/A"
            
            try:
                location = element.find_element(By.CSS_SELECTOR, "div.entity-result__secondary-subtitle").text
                print(f"Found location: {location}")
            except Exception as e:
                print(f"Error finding location: {str(e)}")
                location = "N/A"
            
            if link not in profile_links:
                profile_links.append(link)
                profiles.append({
                    "name": name,
                    "role": role,
                    "location": location,
                    "link": link
                })
        
        if page < 20:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']"))
                )
                human_like_scroll(driver, next_button)
                human_like_click(driver, next_button)
                wait_random('standard')
            except Exception as e:
                print(f"Error clicking next button: {str(e)}")
                break
        
        wait_random('standard')
    print(f"Found {len(profiles)} profiles")
    return profiles  # Return the list of profiles