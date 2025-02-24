import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import logging
import os
import urllib.parse
import re
import asyncio
from playwright.async_api import async_playwright

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MommyPoppinsScraper:
    def __init__(self):
        self.base_url = (
            "https://mommypoppins.com/directory/118/"
            "new-york-city/650/acting-&-theater-classes/"
            "all/age/deals/0/0"
        )
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )
        }
        # Create directory for storing images
        self.image_dir = 'scraped_images'
        os.makedirs(self.image_dir, exist_ok=True)

    def fetch_page(self, url):
        """Fetch page content with error handling and retries"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)

    def download_image(self, image_url, activity_name):
        """Download and save image to local folder."""
        try:
            if not image_url:
                logger.debug(f"No image URL provided for {activity_name}")
                return None

            # Clean filename
            clean_name = re.sub(r'[^a-zA-Z0-9]', '_', activity_name)
            image_ext = image_url.split('.')[-1].split('?')[0]
            filename = f"{clean_name}.{image_ext}"
            filepath = os.path.join(self.image_dir, filename)

            logger.info(f"Downloading image for {activity_name}: {image_url}")

            # Download image
            response = requests.get(image_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            logger.info(f"Successfully saved image to {filepath}")
            return filename

        except Exception as e:
            logger.error(f"Error downloading image for {activity_name}: {str(e)}")
            return None

    async def handle_popups(self, page):
        """Handle common popups and dialogs"""
        try:
            # Common cookie consent selectors
            cookie_buttons = [
                'button[contains(text(), "Accept")]',
                'button[contains(text(), "I agree")]',
                '.cookie-accept',
                '#cookie-consent button',
                '.consent-button'
            ]
            
            for selector in cookie_buttons:
                try:
                    button = await page.wait_for_selector(selector, timeout=5000)
                    if button:
                        await button.click()
                        logger.info(f"Clicked cookie consent button: {selector}")
                        break
                except:
                    continue
                
            # Handle other potential popups
            popup_close_buttons = [
                '.modal-close',
                '.popup-close',
                '.dialog-close'
            ]
            
            for selector in popup_close_buttons:
                try:
                    button = await page.wait_for_selector(selector, timeout=5000)
                    if button:
                        await button.click()
                        logger.info(f"Closed popup using: {selector}")
                except:
                    continue
                
        except Exception as e:
            logger.warning(f"Error handling popups: {str(e)}")

    async def scrape_with_playwright(self):
        """Scrape activities using Playwright for JavaScript rendering"""
        try:
            logger.info("\n=== Starting scraping process with Playwright ===\n")
            
            async with async_playwright() as p:
                # Launch browser with more options
                browser = await p.chromium.launch(
                    headless=False,  # Make browser visible for debugging
                    slow_mo=100  # Slow down operations
                )
                
                # Create context with more realistic browser behavior
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                    viewport={'width': 1280, 'height': 800},
                    ignore_https_errors=True
                )
                
                page = await context.new_page()
                
                # Set longer timeout and more options
                page.set_default_timeout(60000)  # 60 seconds timeout
                page.set_default_navigation_timeout(60000)
                
                # Navigate with more options
                try:
                    await page.goto(
                        self.base_url,
                        wait_until='networkidle',
                        timeout=60000
                    )
                except Exception as e:
                    logger.error(f"Initial navigation failed: {str(e)}")
                    # Try alternative URL or approach
                    alternative_url = "https://mommypoppins.com/new-york-city-kids/directory/camps"
                    await page.goto(
                        alternative_url,
                        wait_until='networkidle',
                        timeout=60000
                    )
                
                # Wait for content with more robust checks
                try:
                    await page.wait_for_selector('#theList', timeout=30000)
                    logger.info("Found main content container")
                except Exception as e:
                    logger.error(f"Could not find main container: {str(e)}")
                    # Try alternative selector
                    await page.wait_for_selector('.directory-listing', timeout=30000)
                
                # Wait for dynamic content
                await page.wait_for_timeout(5000)
                
                await self.handle_popups(page)
                
                # Get the page content after JavaScript execution
                html_content = await page.content()
                
                # Find all JSON-LD scripts
                scripts = await page.query_selector_all('script[type="application/ld+json"]')
                all_activities = []
                
                for script in scripts:
                    try:
                        # Get the text content of the script
                        script_text = await script.text_content()
                        data = json.loads(script_text)
                        
                        if isinstance(data, list):
                            all_activities.extend(data)
                        else:
                            all_activities.append(data)
                    except Exception as e:
                        logger.error(f"Error parsing script: {str(e)}")
                
                await browser.close()
                
                # Filter and process activities
                processed_activities = []
                for item in all_activities:
                    if isinstance(item, dict) and item.get('@type') == 'LocalBusiness':
                        activity = {
                            'name': item.get('name'),
                            'url': item.get('url'),
                            'image_url': item.get('image'),
                            'email': item.get('email'),
                            'position': item.get('position'),
                            'description': item.get('articleBody'),
                            'location': {
                                'name': item.get('location', {}).get('name'),
                                'address': item.get('location', {}).get('address', {}).get('streetAddress'),
                                'city': item.get('location', {}).get('address', {}).get('addressLocality'),
                                'state': item.get('location', {}).get('address', {}).get('addressRegion'),
                                'zip': item.get('location', {}).get('address', {}).get('postalCode'),
                                'phone': item.get('location', {}).get('telephone')
                            }
                        }
                        
                        # Add reviews and ratings
                        if 'review' in item:
                            activity['reviews'] = item['review']
                        if 'aggregateRating' in item:
                            activity['rating'] = item['aggregateRating']
                        
                        # Download image
                        if activity['image_url'] and activity['name']:
                            activity['image_filename'] = self.download_image(
                                activity['image_url'], 
                                activity['name']
                            )
                        
                        processed_activities.append(activity)
                        logger.info(f"Processed: {activity['name']} (Position: {activity['position']})")
                
                # Sort by position
                processed_activities.sort(key=lambda x: int(x.get('position', 999)))
                
                # Save to JSON
                output_file = 'activities_data.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_activities, f, ensure_ascii=False, indent=2)
                    
                logger.info(f"\n=== Scraping Summary ===")
                logger.info(f"Total activities found: {len(processed_activities)}")
                logger.info(f"Data saved to: {output_file}")
                
                return processed_activities
                
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            raise

async def main():
    scraper = MommyPoppinsScraper()
    try:
        activities = await scraper.scrape_with_playwright()
        logger.info(f"Final count of activities: {len(activities)}")
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
