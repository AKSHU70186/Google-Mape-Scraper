import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# Configure Selenium with headless Chrome and user agent
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode (without a GUI)
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
chrome_options.add_argument(f"user-agent={user_agent}")  # Set user agent string

# Update the path to chromedriver as needed
service = Service('/path/to/chromedriver')  # Path to your chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)  # Initialize Chrome webdriver with the specified options

def scrape_google_maps(url):
    """
    Scrape data from the given Google Maps URL.
    
    Args:
        url (str): The URL of the Google Maps page to scrape.
    
    Returns:
        list: A list of dictionaries containing the scraped data.
    """
    try:
        driver.get(url)
        time.sleep(5)  # Allow time for the page to load
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract relevant data
        business_name = soup.find('h1', {'class': 'fontHeadlineLarge'}).text.strip()
        address = soup.find('button', {'data-item-id': 'address'}).text.strip()
        phone_number = soup.find('button', {'data-item-id': 'phone'}).text.strip()
        rating = soup.find('span', {'class': 'section-star-display'}).text.strip()
        reviews = [review.text.strip() for review in soup.find_all('span', {'class': 'section-review-text'})]
        
        return [{
            'Business Name': business_name,
            'Address': address,
            'Phone Number': phone_number,
            'Rating': rating,
            'Reviews': reviews
        }]
    
    except Exception as e:
        print(f"Error scraping the Google Maps page: {e}")
        return None

def store_in_google_sheets(data, spreadsheet_id, json_cred_path):
    """
    Store the scraped data in Google Sheets.
    
    Args:
        data (list): The data to store.
        spreadsheet_id (str): The ID of the Google Sheet.
        json_cred_path (str): The path to the JSON credentials file.
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_cred_path, scope)  # Authenticate using the JSON credentials file
        client = gspread.authorize(creds)  # Authorize the client
        sheet = client.open_by_key(spreadsheet_id).sheet1  # Open the specified Google Sheet

        # Clear existing content
        sheet.clear()
        sheet.insert_row(["Business Name", "Address", "Phone Number", "Rating", "Reviews"], 1)
        for entry in data:
            sheet.append_row([entry['Business Name'], entry['Address'], entry['Phone Number'], entry['Rating'], ', '.join(entry['Reviews'])])

    except Exception as e:
        print(f"Error storing data in Google Sheets: {e}")

# Example usage
url = 'https://maps.google.com/?q=example_location'  # The Google Maps URL to scrape
spreadsheet_id = 'your_google_sheet_id'  # The ID of your Google Sheet
json_cred_path = 'path/to/credentials.json'  # The path to your JSON credentials file
data = scrape_google_maps(url)  # Scrape data from Google Maps
if data:
    store_in_google_sheets(data, spreadsheet_id, json_cred_path)  # Store the data in Google Sheets
    print("Data successfully stored in Google Sheets")
else:
    print("Failed to scrape the Google Maps page")
