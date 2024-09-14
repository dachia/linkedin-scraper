from scrape import setup_driver, scrape_commenters, scrape_profile
from utils import save_profiles_to_csv
import time
import random

def scrape_comment_profile(url, li_at, user_agent):
    driver = setup_driver(li_at, user_agent)

    try:
        # Pause after setting up the driver
        time.sleep(random.uniform(3, 5))

        # Scrape commenters
        commenter_links = scrape_commenters(driver, url)
        
        profiles = []
        for i, link in enumerate(commenter_links, 1):
            print(f"Processing profile {i}/{len(commenter_links)}: {link}")
            profile = scrape_profile(driver, link)
            profiles.append(profile)
            # Wait before processing the next profile to avoid rate limits
            time.sleep(random.uniform(5, 8))  # Increased pause between profile scrapes

        # Pause before saving to CSV
        time.sleep(random.uniform(2, 4))

        # Save profiles to CSV
        save_profiles_to_csv(profiles)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Current page source:")
        print(driver.page_source)

    finally:
        # Pause before closing the browser
        time.sleep(random.uniform(2, 4))
        # Close the browser
        driver.quit()