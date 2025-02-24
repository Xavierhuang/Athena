import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import logging
from pathlib import Path
from playwright.async_api import async_playwright
import asyncio

class WebScrapingTutorial:
    """
    A tutorial class demonstrating web scraping concepts and techniques.
    This class provides step-by-step examples of different scraping methods.
    """
    
    def __init__(self):
        # Set up logging for students to see what's happening
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Example URLs for different scraping scenarios
        self.urls = {
            'basic': 'https://mommypoppins.com/directory/118/new-york-city/650/acting-&-theater-classes/all/age/deals/0/0',
            'pagination': 'https://mommypoppins.com/directory',
            'javascript': 'https://mommypoppins.com/directory/118'
        }
        
    def lesson_1_basic_requests(self):
        """
        Lesson 1: Basic HTTP Requests
        Demonstrates how to make simple HTTP requests and handle responses
        """
        self.logger.info("\n=== Lesson 1: Basic HTTP Requests ===")
        
        try:
            # Basic GET request
            self.logger.info("Making a basic GET request...")
            response = requests.get(self.urls['basic'])
            
            # Check response status
            self.logger.info(f"Response Status Code: {response.status_code}")
            self.logger.info(f"Response Headers: {dict(response.headers)}")
            
            # Handle different status codes
            if response.status_code == 200:
                self.logger.info("Request successful!")
                return response.text
            else:
                self.logger.error(f"Request failed with status code: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Error in lesson 1: {str(e)}")
    
    def lesson_2_parsing_html(self, html_content):
        """
        Lesson 2: Parsing HTML with BeautifulSoup
        Shows how to extract information from HTML structure
        """
        self.logger.info("\n=== Lesson 2: Parsing HTML with BeautifulSoup ===")
        
        try:
            # Create BeautifulSoup object
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Different ways to find elements
            self.logger.info("\nDifferent ways to find elements:")
            self.logger.info("1. Find by ID:")
            main_list = soup.find(id='theList')
            
            self.logger.info("2. Find by Class:")
            items = soup.find_all(class_='list-item directory')
            
            self.logger.info("3. Find by Tag and Attributes:")
            links = soup.find_all('a', href=True)
            
            return {
                'main_list': main_list,
                'items': items,
                'links': links
            }
            
        except Exception as e:
            self.logger.error(f"Error in lesson 2: {str(e)}")
    
    async def lesson_3_javascript_content(self):
        """
        Lesson 3: Handling JavaScript Content
        Demonstrates how to scrape JavaScript-rendered content using Playwright
        """
        self.logger.info("\n=== Lesson 3: Handling JavaScript Content ===")
        
        try:
            async with async_playwright() as p:
                # Launch browser with explanation
                self.logger.info("1. Launching browser...")
                browser = await p.chromium.launch(headless=False)
                
                # Create new page
                self.logger.info("2. Creating new page...")
                page = await browser.new_page()
                
                # Navigate to URL
                self.logger.info("3. Navigating to URL...")
                await page.goto(self.urls['javascript'])
                
                # Wait for content to load
                self.logger.info("4. Waiting for content to load...")
                await page.wait_for_selector('#theList')
                
                # Get page content
                self.logger.info("5. Getting page content...")
                content = await page.content()
                
                await browser.close()
                return content
                
        except Exception as e:
            self.logger.error(f"Error in lesson 3: {str(e)}")
    
    def lesson_4_data_processing(self, data):
        """
        Lesson 4: Processing and Storing Data
        Shows how to clean, structure, and save scraped data
        """
        self.logger.info("\n=== Lesson 4: Data Processing ===")
        
        try:
            # Convert to structured format
            self.logger.info("1. Converting data to structured format...")
            processed_data = []
            for item in data:
                processed_item = {
                    'name': item.get('name'),
                    'url': item.get('url'),
                    'location': item.get('location')
                }
                processed_data.append(processed_item)
            
            # Save as JSON
            self.logger.info("2. Saving as JSON...")
            with open('data/scraped_data.json', 'w') as f:
                json.dump(processed_data, f, indent=2)
            
            # Convert to Excel
            self.logger.info("3. Converting to Excel...")
            df = pd.DataFrame(processed_data)
            df.to_excel('data/scraped_data.xlsx', index=False)
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error in lesson 4: {str(e)}")

async def run_tutorial():
    """Run the complete tutorial"""
    tutorial = WebScrapingTutorial()
    
    # Lesson 1: Basic Requests
    html_content = tutorial.lesson_1_basic_requests()
    
    # Lesson 2: Parsing HTML
    parsed_data = tutorial.lesson_2_parsing_html(html_content)
    
    # Lesson 3: JavaScript Content
    js_content = await tutorial.lesson_3_javascript_content()
    
    # Lesson 4: Data Processing
    if parsed_data and parsed_data['items']:
        tutorial.lesson_4_data_processing(parsed_data['items'])

if __name__ == "__main__":
    asyncio.run(run_tutorial()) 