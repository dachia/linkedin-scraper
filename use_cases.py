from scrape import setup_driver, scrape_commenters, scrape_profile, auto_connect, configure_filters, scrape_search
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

def configure_search_filters(url, li_at, user_agent, filters):
    driver = setup_driver(li_at, user_agent)

    try:
        wait_random()
        # Configure filters
        configure_filters(
            driver,
            url,
            # current_company=filters.get('current_company'),
            current_company=[
                "Bazaar Technologies",
                "Retailo",
                "SadaPay",
                "Tajir",
                # "QisstPay",
                "Jugnu",
                "Oraan",
                "PostEx",
                "Truck It In",
                "Abhi",
                "CreditBook",
                "DigiKhata",
                "Vouch",
                "Krave Mart",
                "Sastaticket.pk",
                "BridgeLinx",
                "BitBlaze",
                "MyTm",
                "Chikoo",
                "Colabs",
                "Careem",
                "Motive",
                "Symantec",
                "Securiti",
                "Overjet",
                "Educative",
                "Laam",
                "Adalfi",
                "Neem"],
            locations=["Pakistan"],
            connections=["1st", "2nd", "3rd"],
            current_role="React native"
        )

        # Get the new URL after applying filters
        new_url = driver.current_url
        wait_random("extra_long")

        return {"success": True, "filtered_url": new_url}

    except Exception as e:
        print(f"An error occurred during filter configuration: {str(e)}")
        return {"success": False, "error": str(e)}

    finally:
        wait_random()
        # driver.quit()

def scrape_search_results(url, li_at, user_agent):  # Renamed function
    driver = setup_driver(li_at, user_agent)

    try:
        wait_random()

        # Scrape profile links
        profile_links = scrape_search(driver, url)  # Updated function call
        
        print(f"Found {len(profile_links)} profile links")
        # Print profile links
        print("Profile links:")
        for link in profile_links:
            print(link)
        print("End of profile links")
        # Save profile links to CSV
        save_profiles_to_csv(profile_links, 'linkedin_profile_links.csv')
        
        return {"success": True, "message": f"Scraped {len(profile_links)} profile links"}

    except Exception as e:
        print(f"An error occurred while scraping search results: {str(e)}")
        return {"success": False, "error": str(e)}

    finally:
        wait_random()
        driver.quit()