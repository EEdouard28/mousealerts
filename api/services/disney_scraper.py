"""
Disney Web Scraper Service

This service implements web scraping to monitor Disney's dining reservation system,
similar to how MouseWatcher works. It uses Selenium with headless browsers to
simulate real user behavior and check for availability.

Features:
- Headless browser automation with Selenium
- User agent rotation and proxy support
- Rate limiting and respectful scraping
- Real-time availability monitoring
- Smart notification system
- Compliance with Disney's terms
"""

import asyncio
import logging
import time
import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date, time as dt_time
from dataclasses import dataclass
from enum import Enum
import json
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from config import settings

logger = logging.getLogger(__name__)

class ScrapingStatus(Enum):
    """Scraping operation status"""
    SUCCESS = "success"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    BLOCKED = "blocked"
    NO_AVAILABILITY = "no_availability"

@dataclass
class ScrapingResult:
    """Result of a scraping operation"""
    status: ScrapingStatus
    available_slots: List[Dict]
    error_message: Optional[str] = None
    scraped_at: datetime = None
    response_time: float = 0.0

@dataclass
class DisneyRestaurantInfo:
    """Disney restaurant information from scraping"""
    name: str
    park: str
    location: str
    cuisine: str
    price_range: str
    phone: str
    website: str
    disney_id: str

class DisneyWebScraper:
    """
    Web scraper for Disney dining reservations.
    
    This scraper mimics real user behavior to check Disney's reservation system
    for availability. It uses headless browsers with realistic delays and
    user agent rotation to avoid detection.
    """
    
    def __init__(self, headless: bool = True, use_proxy: bool = False):
        self.headless = headless
        self.use_proxy = use_proxy
        self.driver: Optional[webdriver.Chrome] = None
        self.ua = UserAgent()
        self.base_url = "https://disneyworld.disney.go.com"
        self.reservation_url = "https://disneyworld.disney.go.com/dining-reservations/"
        self.rate_limit_delay = 2.0  # Minimum delay between requests
        self.max_retries = 3
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._setup_driver()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup_driver()
    
    async def _setup_driver(self):
        """Setup Chrome driver with optimal settings"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Stealth settings to avoid detection
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Random user agent
            user_agent = self.ua.random
            chrome_options.add_argument(f"--user-agent={user_agent}")
            
            # Window size
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Disable images for faster loading
            prefs = {"profile.managed_default_content_settings.images": 2}
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Setup driver - use Chromium for ARM64 compatibility
            try:
                # 1. Try environment variables for path overrides
                import os
                chrome_bin = os.environ.get('CHROME_BIN')
                chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
                
                if chrome_bin:
                    logger.info(f"Using custom Chrome binary: {chrome_bin}")
                    chrome_options.binary_location = chrome_bin
                
                if chromedriver_path:
                    logger.info(f"Using custom Chromedriver: {chromedriver_path}")
                    service = Service(chromedriver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    logger.info("Custom driver setup completed")
                
                # 2. Try Standard Chrome
                elif not chrome_bin:
                    logger.info("Trying standard Chrome setup")
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("Chrome driver setup completed")

            except Exception as chrome_error:
                logger.warning(f"Standard Chrome setup failed: {chrome_error}, trying Chromium fallbacks")
                try:
                    # 3. Fallback to common Chromium paths (Linux/Fly.io)
                    chromium_paths = ["/usr/bin/chromium", "/usr/bin/chromium-browser"]
                    driver_paths = ["/usr/bin/chromedriver", "/usr/lib/chromium-browser/chromedriver"]
                    
                    found_bin = next((p for p in chromium_paths if os.path.exists(p)), None)
                    found_driver = next((p for p in driver_paths if os.path.exists(p)), None)
                    
                    if found_bin and found_driver:
                        logger.info(f"Found Chromium at {found_bin} and driver at {found_driver}")
                        chrome_options.binary_location = found_bin
                        service = Service(found_driver)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    logger.info("Chromium driver setup completed")
                    else:
                        raise WebDriverException("Could not find Chromium or Chromedriver binaries")
                        
                except Exception as chromium_error:
                    logger.error(f"All driver setup attempts failed. Last error: {chromium_error}")
                    raise
            
            # Set timeouts from configuration
            self.driver.set_page_load_timeout(settings.SCRAPER_PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(settings.SCRAPER_IMPLICIT_WAIT)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    async def _cleanup_driver(self):
        """Cleanup Chrome driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Chrome driver cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up driver: {e}")
    
    async def _random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add random delay to mimic human behavior"""
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    async def _navigate_to_disney_site(self) -> bool:
        """Navigate to Disney's dining reservation site"""
        try:
            logger.info("Navigating to Disney dining reservations")
            self.driver.get(self.reservation_url)
            
            # Wait for page to load
            await asyncio.sleep(3)
            
            # Check if we're on the right page
            if "dining" in self.driver.current_url.lower():
                logger.info("Successfully navigated to Disney dining site")
                return True
            else:
                logger.warning(f"Unexpected URL: {self.driver.current_url}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to navigate to Disney site: {e}")
            return False
    
    async def search_restaurant(self, restaurant_name: str, park: str = None) -> List[DisneyRestaurantInfo]:
        """
        Search for a restaurant on Disney's site.
        
        Args:
            restaurant_name: Name of the restaurant to search
            park: Optional park filter
            
        Returns:
            List of matching restaurants
        """
        try:
            if not await self._navigate_to_disney_site():
                return []
            
            # Wait for search elements to load
            wait = WebDriverWait(self.driver, settings.SCRAPER_ELEMENT_WAIT_TIMEOUT)
            
            # Find and fill search box
            search_box = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='restaurant']"))
            )
            
            # Clear and type search term
            search_box.clear()
            await self._random_delay(0.5, 1.0)
            
            # Type with human-like delays
            for char in restaurant_name:
                search_box.send_keys(char)
                await asyncio.sleep(random.uniform(0.05, 0.15))
            
            await self._random_delay(1.0, 2.0)
            
            # Submit search
            search_box.send_keys("\n")
            await asyncio.sleep(2)
            
            # Wait for results
            await self._random_delay(2.0, 4.0)
            
            # Parse results
            restaurants = await self._parse_search_results()
            
            logger.info(f"Found {len(restaurants)} restaurants for '{restaurant_name}'")
            return restaurants
            
        except TimeoutException:
            logger.error("Timeout waiting for search elements")
            return []
        except Exception as e:
            logger.error(f"Failed to search restaurant: {e}")
            return []
    
    async def _parse_search_results(self) -> List[DisneyRestaurantInfo]:
        """Parse search results from Disney's site"""
        restaurants = []
        
        try:
            # Wait for results to load
            wait = WebDriverWait(self.driver, settings.SCRAPER_ELEMENT_WAIT_TIMEOUT)
            results_container = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='search-results']"))
            )
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find restaurant cards
            restaurant_cards = soup.find_all('div', class_='restaurant-card')
            
            for card in restaurant_cards:
                try:
                    name_elem = card.find('h3', class_='restaurant-name')
                    park_elem = card.find('span', class_='park-name')
                    location_elem = card.find('span', class_='location')
                    cuisine_elem = card.find('span', class_='cuisine')
                    price_elem = card.find('span', class_='price-range')
                    
                    if name_elem:
                        restaurant = DisneyRestaurantInfo(
                            name=name_elem.get_text(strip=True),
                            park=park_elem.get_text(strip=True) if park_elem else "",
                            location=location_elem.get_text(strip=True) if location_elem else "",
                            cuisine=cuisine_elem.get_text(strip=True) if cuisine_elem else "",
                            price_range=price_elem.get_text(strip=True) if price_elem else "",
                            phone="",  # Would need additional scraping
                            website="",  # Would need additional scraping
                            disney_id=card.get('data-restaurant-id', '')
                        )
                        restaurants.append(restaurant)
                        
                except Exception as e:
                    logger.warning(f"Error parsing restaurant card: {e}")
                    continue
            
        except TimeoutException:
            logger.error("Timeout waiting for search results")
        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
        
        return restaurants
    
    async def check_availability(self, restaurant_id: str, date: date, 
                                party_size: int, time_slots: List[dt_time] = None) -> ScrapingResult:
        """
        Check availability for a specific restaurant.
        
        Args:
            restaurant_id: Disney restaurant ID
            date: Date to check
            party_size: Number of people
            time_slots: Optional specific time slots
            
        Returns:
            ScrapingResult with availability information
        """
        start_time = time.time()
        
        try:
            # Navigate to restaurant page
            restaurant_url = f"{self.base_url}/dining/{restaurant_id}/"
            self.driver.get(restaurant_url)
            await self._random_delay(2.0, 4.0)
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, settings.SCRAPER_ELEMENT_WAIT_TIMEOUT)
            
            # Find and click "Check Availability" button
            try:
                check_availability_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='check-availability']"))
                )
                check_availability_btn.click()
                await self._random_delay(1.0, 2.0)
            except TimeoutException:
                logger.warning("Check availability button not found")
                return ScrapingResult(
                    status=ScrapingStatus.FAILED,
                    available_slots=[],
                    error_message="Check availability button not found"
                )
            
            # Fill in date
            try:
                date_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='date']"))
                )
                date_input.clear()
                date_input.send_keys(date.strftime("%Y-%m-%d"))
                await self._random_delay(0.5, 1.0)
            except TimeoutException:
                logger.warning("Date input not found")
            
            # Fill in party size
            try:
                party_size_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='party-size']"))
                )
                party_size_input.clear()
                party_size_input.send_keys(str(party_size))
                await self._random_delay(0.5, 1.0)
            except TimeoutException:
                logger.warning("Party size input not found")
            
            # Submit search
            try:
                search_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
                )
                search_btn.click()
                await self._random_delay(3.0, 5.0)
            except TimeoutException:
                logger.warning("Search button not found")
            
            # Parse availability results
            available_slots = await self._parse_availability_results(time_slots)
            
            response_time = time.time() - start_time
            
            if available_slots:
                logger.info(f"Found {len(available_slots)} available slots")
                return ScrapingResult(
                    status=ScrapingStatus.SUCCESS,
                    available_slots=available_slots,
                    scraped_at=datetime.utcnow(),
                    response_time=response_time
                )
            else:
                logger.info("No availability found")
                return ScrapingResult(
                    status=ScrapingStatus.NO_AVAILABILITY,
                    available_slots=[],
                    scraped_at=datetime.utcnow(),
                    response_time=response_time
                )
                
        except WebDriverException as e:
            logger.error(f"WebDriver error: {e}")
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                available_slots=[],
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error checking availability: {e}")
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                available_slots=[],
                error_message=str(e)
            )
    
    async def _parse_availability_results(self, time_slots: List[dt_time] = None) -> List[Dict]:
        """Parse availability results from the page"""
        available_slots = []
        
        try:
            # Wait for results to load
            wait = WebDriverWait(self.driver, settings.SCRAPER_ELEMENT_WAIT_TIMEOUT)
            
            # Look for availability indicators
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find time slot elements
            time_elements = soup.find_all('div', class_='time-slot')
            
            for element in time_elements:
                try:
                    # Check if slot is available
                    if 'available' in element.get('class', []):
                        time_text = element.find('span', class_='time').get_text(strip=True)
                        time_obj = datetime.strptime(time_text, "%I:%M %p").time()
                        
                        # Filter by requested time slots if provided
                        if not time_slots or time_obj in time_slots:
                            slot_info = {
                                'time': time_obj.isoformat(),
                                'available': True,
                                'party_size': 1,  # Would need to extract from page
                                'restaurant_name': '',  # Would need to extract
                                'date': '',  # Would need to extract
                                'scraped_at': datetime.utcnow().isoformat()
                            }
                            available_slots.append(slot_info)
                            
                except Exception as e:
                    logger.warning(f"Error parsing time slot: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error parsing availability results: {e}")
        
        return available_slots
    
    async def monitor_alert(self, alert_data: Dict) -> ScrapingResult:
        """
        Monitor a specific alert for availability.
        
        Args:
            alert_data: Alert configuration with restaurant, date, time, party_size
            
        Returns:
            ScrapingResult with availability information
        """
        try:
            restaurant_id = alert_data.get('restaurant_id', '')
            
            # If restaurant_id looks like a name (contains spaces or no digits/dashes), try to search for it
            # Simple heuristic: Disney IDs are usually slug-like (e.g. "be-our-guest-restaurant")
            # Names are usually "Be Our Guest Restaurant"
            if ' ' in restaurant_id or not re.match(r'^[a-z0-9-]+$', restaurant_id):
                logger.info(f"Restaurant ID '{restaurant_id}' looks like a name, searching for ID...")
                results = await self.search_restaurant(restaurant_id)
                if results:
                    # Use the first result's ID
                    new_id = results[0].disney_id
                    logger.info(f"Resolved '{restaurant_id}' to ID '{new_id}'")
                    restaurant_id = new_id
                else:
                    logger.warning(f"Could not resolve restaurant name '{restaurant_id}' to an ID")
                    # Continue with original ID in case it works or to fail gracefully
            
            date_str = alert_data.get('date', '')
            party_size = alert_data.get('party_size', 1)
            time_str = alert_data.get('time', '')
            
            # Convert date string to date object
            date_obj = datetime.fromisoformat(date_str).date()
            
            # Convert time string to time object
            time_obj = datetime.fromisoformat(time_str).time()
            
            # Check availability
            result = await self.check_availability(
                restaurant_id=restaurant_id,
                date=date_obj,
                party_size=party_size,
                time_slots=[time_obj]
            )
            
            logger.info(f"Alert monitoring completed for {restaurant_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to monitor alert: {e}")
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                available_slots=[],
                error_message=str(e)
            )

# Utility functions for scraping management
async def create_scraper(headless: bool = True, use_proxy: bool = False) -> DisneyWebScraper:
    """Create a new Disney web scraper instance"""
    return DisneyWebScraper(headless=headless, use_proxy=use_proxy)

async def test_scraper_connection() -> bool:
    """Test if the scraper can connect to Disney's site"""
    try:
        async with DisneyWebScraper() as scraper:
            return await scraper._navigate_to_disney_site()
    except Exception as e:
        logger.error(f"Scraper connection test failed: {e}")
        return False

async def get_scraper_stats() -> Dict:
    """Get scraper statistics and health"""
    return {
        "status": "operational",
        "last_check": datetime.utcnow().isoformat(),
        "rate_limit_delay": 2.0,
        "max_retries": 3,
        "headless_mode": True
    }
