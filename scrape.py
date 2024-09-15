import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import math
from utils import wait_random, navigate_to_url

def setup_driver(li_at, user_agent):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument(f'user-agent={user_agent}')
    
    # Set up the WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the domain for which you want to set cookies
    navigate_to_url(driver, "https://www.linkedin.com")
    print("Navigated to LinkedIn homepage")

    # Set cookies
    cookies = {
        'li_at': li_at,
    }

    for name, value in cookies.items():
        driver.add_cookie({'name': name, 'value': value})
    print("Cookies set")

    return driver

def human_like_mouse_move(driver, element):
    action = ActionChains(driver)
    action.move_to_element_with_offset(element, 0, 0)
    
    # Generate a random number of intermediate points
    num_steps = random.randint(5, 10)
    
    for _ in range(num_steps):
        x_offset = random.randint(-50, 50)
        y_offset = random.randint(-50, 50)
        action.move_by_offset(x_offset, y_offset)
    
    action.move_to_element(element)
    action.perform()
    wait_random('short')

def get_header_height(driver):
    try:
        header = driver.find_element(By.CSS_SELECTOR, "section.scaffold-layout-toolbar")
        return header.rect['height'] + 20  # Added a buffer of 20 pixels
    except NoSuchElementException:
        print("Header not found. Returning default height.")
        return 70  # Default height if header is not found

def is_element_in_viewport(driver, element):
    """Check if an element is in the viewport with some offsets."""
    return driver.execute_script("""
        var rect = arguments[0].getBoundingClientRect();
        var offset = 50;  // Offset in pixels
        return (
            rect.top >= offset &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) - offset &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    """, element)

def human_like_scroll(driver, element):
    print(f"Attempting to scroll to element: {element.tag_name}")
    
    # Check if the element is already in the viewport
    if is_element_in_viewport(driver, element):
        print("Element is already in viewport. No need to scroll.")
        return

    header_height = get_header_height(driver)
    target_y = element.location['y']
    viewport_height = driver.execute_script("return window.innerHeight")
    current_y = driver.execute_script("return window.pageYOffset")
    
    print(f"Current scroll position: {current_y}")
    print(f"Target scroll position: {target_y}")
    
    # Adjust target_y to account for header
    target_y = max(0, target_y - header_height - 50)  # 50px extra buffer
    print(f"Adjusted target scroll position: {target_y}")

    # Scroll until the target position is reached or the element is unloaded
    while current_y < target_y:
        scroll_amount = min(random.randint(200, 500), target_y - current_y)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        print(f"Scrolled by {scroll_amount} pixels")
        wait_random('short')
        current_y = driver.execute_script("return window.pageYOffset")
        print(f"New scroll position: {current_y}")

        # Check if the element is still in the DOM and its position has not changed
        try:
            # Check if the element is now in the viewport
            if is_element_in_viewport(driver, element):
                print("Element is now in view. Stopping scroll.")
                break
            
            new_target_y = element.location['y']
            if new_target_y != target_y:
                print("Element position has changed. Updating target position.")
                target_y = max(0, new_target_y - header_height - 50)  # Update target_y
                print(f"New target scroll position: {target_y}")
        except NoSuchElementException:
            print("Element has been unloaded from the DOM. Stopping scroll.")
            break

    # Final adjustment to ensure the element is in view
    if not is_element_in_viewport(driver, element):
        print("Element still not in view. Performing final adjustment.")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", element)
        wait_random('short')
        print("Final adjustment completed.")
    else:
        print("Element is now in view.")

def human_like_click(driver, element):
    human_like_mouse_move(driver, element)
    element.click()
    wait_random('short')

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

def close_modal(driver):
    try:
        # Try clicking the close button first
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss' and @data-test-modal-close-btn]"))
        )
        human_like_click(driver, close_button)
        print("Closed the modal using the close button.")
    except Exception as e:
        print(f"Error clicking close button: {str(e)}")
        try:
            # If clicking the button fails, try clicking outside the modal
            modal_backdrop = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".artdeco-modal-overlay"))
            )
            action = ActionChains(driver)
            action.move_to_element_with_offset(modal_backdrop, 1, 1).click().perform()
            print("Closed the modal by clicking outside.")
        except Exception as e2:
            print(f"Error clicking outside modal: {str(e2)}")
            # As a last resort, try using JavaScript
            driver.execute_script("""
                var closeButton = document.querySelector('button[aria-label="Dismiss"][data-test-modal-close-btn]');
                if (closeButton) {
                    closeButton.click();
                } else {
                    var modalBackdrop = document.querySelector('.artdeco-modal-overlay');
                    if (modalBackdrop) {
                        modalBackdrop.click();
                    }
                }
            """)
            print("Attempted to close the modal using JavaScript.")
    
    wait_random('short')

def human_like_scroll_page(driver):
    # Get the total height of the page
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    
    # Scroll down
    current_position = 0
    while current_position < total_height:
        scroll_amount = random.randint(300, 700)  # Increased scroll amount
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        current_position += scroll_amount
        wait_random('short')
    
    # Short pause at the bottom
    wait_random('short')  # Changed from 'standard' to 'short'
    
    # Scroll back up
    while current_position > 0:
        scroll_amount = random.randint(300, 700)  # Increased scroll amount
        driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
        current_position -= scroll_amount
        wait_random('short')

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
def hide_chat(driver):
    print("Attempting to hide chat")
    try:
        # Wait for the hide chat button to be clickable
        hide_chat_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'msg-overlay-bubble-header__control') and contains(@class, 'msg-overlay-bubble-header__control--new-convo-btn') and .//svg[@data-test-icon='chevron-down-small']]"))
        )
        print("Found hide chat button")
        
        # Scroll to the button if necessary
        # human_like_scroll(driver, hide_chat_button)
        
        # Click the button
        human_like_click(driver, hide_chat_button)
        print("Successfully clicked hide chat button")
        
        # Wait for the chat to be hidden
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.XPATH, "//aside[contains(@class, 'msg-overlay-list-bubble')]"))
        )
        print("Chat hidden successfully")
    except TimeoutException:
        print("Hide chat button not found or not clickable")
    except Exception as e:
        print(f"Error hiding chat: {str(e)}")

def accept_cookies(driver):
    print("Attempting to accept cookies")
    try:
        # Wait for the accept cookies button to be clickable
        accept_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-test-global-alert-action='0' and contains(@class, 'artdeco-global-alert__action')]"))
        )
        
        # Check if the button is in the viewport
        if not is_element_in_viewport(driver, accept_button):
            print("Accept cookies button is not in viewport. Attempting to scroll.")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", accept_button)
            wait_random('short')
        
        # Try to click using JavaScript if regular click fails
        try:
            human_like_click(driver, accept_button)
        except Exception as e:
            print(f"Regular click failed: {str(e)}. Attempting JavaScript click.")
            driver.execute_script("arguments[0].click();", accept_button)
        
        print("Successfully clicked accept cookies button")
        
        # Wait for the cookie banner to disappear
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.XPATH, "//div[contains(@class, 'artdeco-global-alert')]"))
        )
        print("Cookies accepted successfully")
    except TimeoutException:
        print("Accept cookies button not found or not clickable")
    except Exception as e:
        print(f"Error accepting cookies: {str(e)}")
        # If all else fails, try to dismiss using JavaScript
        try:
            driver.execute_script("""
                var elements = document.getElementsByClassName('artdeco-global-alert__action');
                for(var i=0; i<elements.length; i++) {
                    if(elements[i].textContent.includes('Accept')) {
                        elements[i].click();
                        break;
                    }
                }
            """)
            print("Attempted to accept cookies using JavaScript")
        except Exception as js_error:
            print(f"JavaScript cookie acceptance failed: {str(js_error)}")

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
    
    # Set past company
    # if past_company:
    #     print(f"Setting past company filter: {past_company}")
    #     set_company_filter(driver, "past-company-filter-value", past_company)
    
    # Set locations
    # if locations:
    #     print(f"Setting location filters: {locations}")
    #     set_location_filter(driver, locations)
    
    # # Set connections
    # if connections:
    #     print(f"Setting connections filters: {connections}")
    #     set_connections_filter(driver, connections)
    
    # # Set current role
    # if current_role:
    #     print(f"Setting current role filter: {current_role}")
    #     set_current_role_filter(driver, current_role)
    
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

def set_location_filter(driver, locations):
    for location in locations:
        location_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='locations-filter-value']/../following-sibling::button"))
        )
        human_like_click(driver, location_input)
        
        location_search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Add a location']"))
        )
        location_search.send_keys(location)
        
        wait_random('short')
        
        location_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'basic-typeahead__selectable')]//span[text()='{location}']"))
        )
        human_like_click(driver, location_option)

def set_connections_filter(driver, connections):
    for connection in connections:
        connection_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'search-reusables__multiselect-pill-button') and contains(., '{connection}')]"))
        )
        human_like_click(driver, connection_button)

def set_current_role_filter(driver, role):
    title_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Title']"))
    )
    title_input.send_keys(role)

    print(f"Auto-connect process completed. Processed {pages_processed} pages.")