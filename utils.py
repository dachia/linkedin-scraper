import time
import random
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

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
    fieldnames = profiles[0].keys() if profiles else []
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for profile in profiles:
            writer.writerow(profile)    
    print(f"Profiles saved to {filename}")

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
        var topOffset = 50;  // Offset in pixels from the top
        var bottomOffset = 50;  // Offset in pixels from the bottom
        return (
            rect.top >= topOffset &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) - bottomOffset &&
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

def close_modal(driver):
    print("Attempting to close modal")
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

def hide_chat(driver):
    print("Attempting to hide chat")
    try:
        # Wait for the hide chat button to be clickable
        hide_chat_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'msg-overlay-bubble-header__control') and contains(@class, 'msg-overlay-bubble-header__control--new-convo-btn') and .//svg[@data-test-icon='chevron-down-small']]"))
        )
        print("Found hide chat button")
        
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

