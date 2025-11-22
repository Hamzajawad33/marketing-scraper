from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
import requests
import re
from urllib.parse import urlparse
from .utils import get_random_user_agent


class ScraperEngine:
    """Main scraper engine for extracting business data from Google Maps."""
    
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.results = []
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with options and user agent rotation."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
        
        user_agent = get_random_user_agent()
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # Anti-detection
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def search(self, keyword, location):
        try:
            query = f"{keyword} in {location}"
            url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
            print(f"Searching for: {query}")
            self.driver.get(url)
            time.sleep(3)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            return True
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return False
    
    def scroll_and_collect(self, max_results=20, should_stop=None):
        try:
            results_container = self.driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            business_elements = []
            last_count = 0
            scroll_attempts = 0
            
            print("Scrolling to load results...")
            while len(business_elements) < max_results and scroll_attempts < 50:
                if should_stop and should_stop():
                    print("Scraping aborted during scrolling.")
                    return []

                business_elements = results_container.find_elements(By.CSS_SELECTOR, "div[role='article']")
                current_count = len(business_elements)
                
                if current_count == last_count:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                    last_count = current_count
                
                if business_elements:
                    self.driver.execute_script("arguments[0].scrollIntoView();", business_elements[-1])
                    time.sleep(random.uniform(1, 2))
            
            return business_elements[:max_results]
        except Exception as e:
            print(f"Error during scrolling: {str(e)}")
            return []

    def analyze_website(self, url, should_stop=None):
        """
        Deep scan of the business website to extract advanced marketing data.
        Returns a dictionary of findings.
        """
        data = {
            'Social_Facebook': '', 'Social_Instagram': '', 'Social_LinkedIn': '', 'Social_Twitter': '',
            'Email_Found': '', 'Ad_Pixel_FB': 'No', 'Ad_Pixel_Google': 'No',
            'SEO_Title': '', 'SEO_Description': '', 'SSL_Secure': 'No', 'Mobile_Friendly': 'Unknown'
        }
        
        if not url:
            return data

        if should_stop and should_stop():
            return data

        try:
            # Check SSL
            if url.startswith('https'):
                data['SSL_Secure'] = 'Yes'
            
            # Request the page
            headers = {'User-Agent': get_random_user_agent()}
            
            if should_stop and should_stop():
                return data

            response = requests.get(url, headers=headers, timeout=10)
            
            if should_stop and should_stop():
                return data

            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = response.text.lower()
            
            # 1. Social Media Links
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            for link in links:
                if 'facebook.com' in link: data['Social_Facebook'] = link
                elif 'instagram.com' in link: data['Social_Instagram'] = link
                elif 'linkedin.com' in link: data['Social_LinkedIn'] = link
                elif 'twitter.com' in link or 'x.com' in link: data['Social_Twitter'] = link
                elif 'mailto:' in link: 
                    data['Email_Found'] = link.replace('mailto:', '').split('?')[0]

            # 2. Ad Pixels (Regex search in scripts)
            if 'fbevents.js' in text_content or 'fbq(' in text_content:
                data['Ad_Pixel_FB'] = 'Yes'
            if 'gtag(' in text_content or 'google-analytics.com' in text_content:
                data['Ad_Pixel_Google'] = 'Yes'
                
            # 3. SEO Health
            if soup.title:
                data['SEO_Title'] = soup.title.string.strip()[:100]
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                data['SEO_Description'] = meta_desc.get('content', '').strip()[:150]
                
            # 4. Mobile Friendly (Check for viewport meta tag)
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if viewport:
                data['Mobile_Friendly'] = 'Yes'
            else:
                data['Mobile_Friendly'] = 'No'
                
        except Exception as e:
            print(f"  [Website Analysis Failed] {e}")
            
        return data

    def extract_details(self, business_elements, keyword, location, should_stop=None):
        businesses = []
        urls_to_process = []
        
        print(f"\n[PHASE 1] Collecting URLs from {len(business_elements)} listings...")
        
        for i, element in enumerate(business_elements):
            if should_stop and should_stop():
                print("Scraping aborted during URL collection.")
                return businesses

            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(0.1)
                try:
                    link = element.find_element(By.CSS_SELECTOR, "a.hfpxzc")
                    url = link.get_attribute('href')
                    if url: urls_to_process.append(url)
                except: pass
            except: continue
        
        print(f"\n[PHASE 2] Extracting details from {len(urls_to_process)} businesses...")
        
        for i, url in enumerate(urls_to_process):
            if should_stop and should_stop():
                print("Scraping aborted during detail extraction.")
                return businesses

            try:
                print(f"\nProcessing {i+1}/{len(urls_to_process)}: {url[:60]}...")
                self.driver.get(url)
                time.sleep(random.uniform(2, 4))
                
                # Basic Data
                business_data = {
                    'Business Name': '', 'Category': '', 'Phone': '', 'Email': '', 'Website': '',
                    'Address': '', 'Rating': '', 'Reviews': '', 'Keyword': keyword, 'City': location,
                    'Claimed_Status': 'Unknown', 'Business_Hours': '', 'Coordinates': '',
                    # Advanced fields will be merged here
                }
                
                # 1. Name
                try: business_data['Business Name'] = self.driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
                except: pass
                
                # 2. Rating/Reviews
                try: business_data['Rating'] = self.driver.find_element(By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']").text.strip()
                except: pass
                try: business_data['Reviews'] = self.driver.find_element(By.CSS_SELECTOR, "span[aria-label*='reviews']").get_attribute("aria-label").split()[0].replace(',','')
                except: pass
                
                # 3. Category
                try: business_data['Category'] = self.driver.find_element(By.CSS_SELECTOR, "button.DkEaL").text.strip()
                except: pass
                
                # 4. Claimed Status
                try:
                    self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id*='merchant']")
                    business_data['Claimed_Status'] = 'Unclaimed' # If button exists, it's likely "Claim this business"
                except:
                    business_data['Claimed_Status'] = 'Claimed'

                # 5. Coordinates (from URL)
                try:
                    curr_url = self.driver.current_url
                    coords = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', curr_url)
                    if coords:
                        business_data['Coordinates'] = f"{coords.group(1)}, {coords.group(2)}"
                except: pass

                # 6. Buttons (Phone, Website, Address)
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[data-item-id], a[data-item-id]")
                    for btn in buttons:
                        aria = btn.get_attribute("aria-label") or ""
                        href = btn.get_attribute("href") or ""
                        data_id = btn.get_attribute("data-item-id") or ""
                        
                        if "phone" in data_id or "tel:" in href:
                            business_data['Phone'] = aria.replace("Phone: ", "") or btn.text.strip()
                        elif "authority" in data_id or "http" in href:
                            if "google" not in href: business_data['Website'] = href
                        elif "address" in data_id:
                            business_data['Address'] = aria.replace("Address: ", "") or btn.text.strip()
                except: pass
                
                # 7. Business Hours (Simple extraction)
                try:
                    hours_btn = self.driver.find_element(By.CSS_SELECTOR, "div[aria-label*='Open']" or "div[aria-label*='Closed']")
                    business_data['Business_Hours'] = hours_btn.get_attribute("aria-label")
                except: pass

                # 8. Deep Website Analysis (The 10 Advanced Features)
                if business_data['Website']:
                    print(f"  Analyzing Website: {business_data['Website']}...")
                    analysis = self.analyze_website(business_data['Website'], should_stop=should_stop)
                    business_data.update(analysis)
                    # Fallback for email if not found on site
                    if not business_data['Email'] and analysis['Email_Found']:
                        business_data['Email'] = analysis['Email_Found']
                else:
                    # Fill empty advanced fields
                    defaults = {
                        'Social_Facebook': '', 'Social_Instagram': '', 'Social_LinkedIn': '', 'Social_Twitter': '',
                        'Email_Found': '', 'Ad_Pixel_FB': 'No', 'Ad_Pixel_Google': 'No',
                        'SEO_Title': '', 'SEO_Description': '', 'SSL_Secure': 'No', 'Mobile_Friendly': 'Unknown'
                    }
                    business_data.update(defaults)

                if business_data['Business Name']:
                    businesses.append(business_data)
                    print(f"  [SUCCESS] {business_data['Business Name']}")
                    
            except Exception as e:
                print(f"  Error processing URL {url}: {e}")
                continue
                
        return businesses
    
    def scrape_with_filter(self, keyword, location, max_results, filter_func, should_stop=None):
        """
        Smart scraping: continues scrolling and extracting until 'max_results' 
        businesses passing 'filter_func' are found.
        """
        valid_businesses = []
        processed_urls = set()
        
        try:
            results_container = self.driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
            scroll_attempts = 0
            last_count = 0
            
            print(f"Smart Filter Active: Searching for {max_results} qualified businesses...")
            
            while len(valid_businesses) < max_results and scroll_attempts < 50:
                if should_stop and should_stop():
                    print("Scraping aborted.")
                    return valid_businesses

                # 1. Collect current elements
                elements = results_container.find_elements(By.CSS_SELECTOR, "div[role='article']")
                current_count = len(elements)
                
                # 2. Process new elements
                # We only process elements we haven't seen (or process all and skip by URL)
                # Since we don't have URLs yet, we'll try to process the last batch
                
                # Strategy: Process the last N elements that we haven't processed yet
                # But since we can't easily track elements by ID, we'll just try to process the new ones
                # Or simpler: Process everything currently visible that hasn't been processed?
                # Better: Just grab all URLs first? No, we need to extract details to filter.
                
                # Let's iterate backwards from the end to find new ones?
                # Or just iterate through all and skip if URL in processed_urls
                
                print(f"  Scanning {len(elements)} loaded listings...")
                
                for element in elements:
                    if len(valid_businesses) >= max_results:
                        break
                        
                    if should_stop and should_stop():
                        return valid_businesses

                    try:
                        # Get URL to check if processed
                        try:
                            link = element.find_element(By.CSS_SELECTOR, "a.hfpxzc")
                            url = link.get_attribute('href')
                        except:
                            continue
                            
                        if not url or url in processed_urls:
                            continue
                            
                        processed_urls.add(url)
                        
                        # Extract details for this single business
                        print(f"  Checking: {url[:40]}...")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        
                        # We need to click or navigate to get details? 
                        # The current extract_details navigates to the URL.
                        # So we should do that here too.
                        
                        # Save current handle to return to list?
                        # Google Maps is SPA, navigating away might lose the list state unless we open in new tab.
                        # OR: The current extract_details does `self.driver.get(url)`. This resets the list!
                        # CRITICAL: If we navigate away, we lose the scroll position and the list!
                        
                        # SOLUTION: We must collect a batch of URLs, process them, and if we don't have enough,
                        # we must RE-SEARCH and scroll down to where we left off? That's hard.
                        # ALTERNATIVE: Open in new tab?
                        
                        # Let's try opening in new tab.
                        self.driver.execute_script("window.open('');")
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        
                        try:
                            self.driver.get(url)
                            time.sleep(random.uniform(1.5, 3))
                            
                            # Extract Data (Reuse logic? It's embedded in extract_details loop)
                            # Let's extract a helper method for single business extraction later?
                            # For now, inline the extraction logic or call a helper if I can make one.
                            # I'll copy the extraction logic for safety to avoid breaking existing method.
                            
                            business_data = self._extract_single_business(keyword, location, url, should_stop)
                            
                            if business_data:
                                # Apply Filter
                                if filter_func(business_data):
                                    valid_businesses.append(business_data)
                                    print(f"  [MATCH] Found {len(valid_businesses)}/{max_results}: {business_data.get('Business Name')}")
                                else:
                                    print(f"  [SKIP] Filter criteria not met.")
                                    
                        finally:
                            # Close tab and return to list
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                            
                    except Exception as e:
                        print(f"Error processing element: {e}")
                        continue

                # 3. Scroll for more if needed
                if len(valid_businesses) < max_results:
                    if current_count == last_count:
                        scroll_attempts += 1
                    else:
                        scroll_attempts = 0
                        last_count = current_count
                        
                    if elements:
                        self.driver.execute_script("arguments[0].scrollIntoView();", elements[-1])
                        time.sleep(random.uniform(1.5, 2.5))
                        
            return valid_businesses
            
        except Exception as e:
            print(f"Error during smart scraping: {str(e)}")
            return valid_businesses

    def _extract_single_business(self, keyword, location, url, should_stop):
        """Helper to extract data for a single business from current page."""
        try:
            business_data = {
                'Business Name': '', 'Category': '', 'Phone': '', 'Email': '', 'Website': '',
                'Address': '', 'Rating': '', 'Reviews': '', 'Keyword': keyword, 'City': location,
                'Claimed_Status': 'Unknown', 'Business_Hours': '', 'Coordinates': '',
            }
            
            # 1. Name
            try: business_data['Business Name'] = self.driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
            except: pass
            
            # 2. Rating/Reviews
            try: business_data['Rating'] = self.driver.find_element(By.CSS_SELECTOR, "div.F7nice span[aria-hidden='true']").text.strip()
            except: pass
            try: business_data['Reviews'] = self.driver.find_element(By.CSS_SELECTOR, "span[aria-label*='reviews']").get_attribute("aria-label").split()[0].replace(',','')
            except: pass
            
            # 3. Category
            try: business_data['Category'] = self.driver.find_element(By.CSS_SELECTOR, "button.DkEaL").text.strip()
            except: pass
            
            # 4. Claimed Status
            try:
                self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id*='merchant']")
                business_data['Claimed_Status'] = 'Unclaimed'
            except:
                business_data['Claimed_Status'] = 'Claimed'

            # 5. Coordinates
            try:
                curr_url = self.driver.current_url
                coords = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', curr_url)
                if coords:
                    business_data['Coordinates'] = f"{coords.group(1)}, {coords.group(2)}"
            except: pass

            # 6. Buttons (Phone, Website, Address)
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[data-item-id], a[data-item-id]")
                for btn in buttons:
                    aria = btn.get_attribute("aria-label") or ""
                    href = btn.get_attribute("href") or ""
                    data_id = btn.get_attribute("data-item-id") or ""
                    
                    if "phone" in data_id or "tel:" in href:
                        business_data['Phone'] = aria.replace("Phone: ", "") or btn.text.strip()
                    elif "authority" in data_id or "http" in href:
                        if "google" not in href: business_data['Website'] = href
                    elif "address" in data_id:
                        business_data['Address'] = aria.replace("Address: ", "") or btn.text.strip()
            except: pass
            
            # 7. Business Hours
            try:
                hours_btn = self.driver.find_element(By.CSS_SELECTOR, "div[aria-label*='Open']" or "div[aria-label*='Closed']")
                business_data['Business_Hours'] = hours_btn.get_attribute("aria-label")
            except: pass

            # 8. Deep Website Analysis
            if business_data['Website']:
                # print(f"  Analyzing Website: {business_data['Website']}...") 
                # Optimization: Only analyze if we're keeping it? 
                # No, we might filter based on analysis results (though currently only filtering on existence of website)
                # For "No Website" filter, if it has a website, we discard it anyway, so no need to analyze!
                
                # But if we had other filters, we might need it.
                # For now, let's defer analysis until AFTER filter check in the main loop?
                # The filter_func checks 'Website' field.
                pass
            else:
                defaults = {
                    'Social_Facebook': '', 'Social_Instagram': '', 'Social_LinkedIn': '', 'Social_Twitter': '',
                    'Email_Found': '', 'Ad_Pixel_FB': 'No', 'Ad_Pixel_Google': 'No',
                    'SEO_Title': '', 'SEO_Description': '', 'SSL_Secure': 'No', 'Mobile_Friendly': 'Unknown'
                }
                business_data.update(defaults)

            return business_data
        except:
            return None

    def close(self):
        if self.driver:
            self.driver.quit()
            print("Browser closed")
