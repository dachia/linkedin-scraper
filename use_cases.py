from scrape import setup_driver, scrape_commenters, scrape_profile
from utils import save_profiles_to_csv
import time

def scrape_comment_profile(url, li_at):
    driver = setup_driver(li_at)

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
# linkedin_url = "https://www.linkedin.com/posts/gisenberg_i-just-uploaded-a-new-podcast-with-jason-activity-7238939519310331905-HrIa"
# scrape_comment_profile(linkedin_url)