import csv

def save_profiles_to_csv(profiles, filename='linkedin_profiles.csv'):
    fieldnames = ['name', 'role', 'email', 'phone', 'link']
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for profile in profiles:
            writer.writerow(profile)
    
    print(f"Profiles saved to {filename}")