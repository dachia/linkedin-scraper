from scrape import setup_driver, scrape_commenters, scrape_profile, auto_connect
from utils import save_profiles_to_csv, wait_random

def scrape_comment_profile(url, li_at, user_agent):
    driver = setup_driver(li_at, user_agent)

    try:
        wait_random()

        # Scrape commenters
        commenter_links = scrape_commenters(driver, url)
        
        profiles = []
        for i, link in enumerate(commenter_links, 1):
            print(f"Processing profile {i}/{len(commenter_links)}: {link}")
            profile = scrape_profile(driver, link)
            profiles.append(profile)
            wait_random('long')  # Longer pause between profile scrapes

        wait_random()

        # Save profiles to CSV
        save_profiles_to_csv(profiles)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Current page source:")
        # print(driver.page_source)

    finally:
        wait_random()
        driver.quit()

def auto_connect_profiles(url, li_at, user_agent, max_pages=10):
    driver = setup_driver(li_at, user_agent)

    try:
        wait_random()

        # Call the auto_connect function
        auto_connect(driver, url, max_pages)

    except Exception as e:
        print(f"An error occurred during auto-connect: {str(e)}")
        print("Current page source:")
        # print(driver.page_source)

    finally:
        wait_random()
        driver.quit()