"""
Debug script to inspect Google Maps detail panel HTML
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Search
    query = "car wash in boston"
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    
    print(f"Opening: {url}")
    driver.get(url)
    time.sleep(5)
    
    # Wait for results
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
    )
    
    # Get first business element
    results_container = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
    business_elements = results_container.find_elements(By.CSS_SELECTOR, "div[role='article']")
    
    print(f"\nFound {len(business_elements)} businesses")
    
    if business_elements:
        element = business_elements[0]
        
        # Click on the first business
        print("\nClicking on first business...")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", element)
        time.sleep(4)
        
        print("\n" + "="*60)
        print("DETAIL PANEL LOADED")
        print("="*60)
        
        # Try to find the detail panel
        try:
            detail_panel = driver.find_element(By.CSS_SELECTOR, "div[role='main']")
            print("\nFound detail panel with role='main'")
            
            # Scroll in detail panel
            driver.execute_script("arguments[0].scrollTop = 200;", detail_panel)
            time.sleep(1)
            
            # Save the HTML
            panel_html = detail_panel.get_attribute('outerHTML')
            with open('detail_panel.html', 'w', encoding='utf-8') as f:
                f.write(panel_html)
            print("Saved detail panel HTML to detail_panel.html")
            
        except Exception as e:
            print(f"Error finding detail panel: {e}")
        
        # Try to find specific elements
        print("\n" + "="*60)
        print("SEARCHING FOR SPECIFIC ELEMENTS")
        print("="*60)
        
        # Look for phone
        phone_selectors = [
            "button[data-item-id*='phone']",
            "button[aria-label*='Phone']",
            "a[href^='tel:']",
            "[data-item-id*='phone']"
        ]
        
        print("\n--- PHONE ---")
        for selector in phone_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"FOUND: {selector}")
                print(f"  Text: {elem.text}")
                print(f"  aria-label: {elem.get_attribute('aria-label')}")
                print(f"  href: {elem.get_attribute('href')}")
                break
            except:
                print(f"NOT FOUND: {selector}")
        
        # Look for address
        address_selectors = [
            "button[data-item-id='address']",
            "button[aria-label*='Address']",
            "[data-item-id='address']"
        ]
        
        print("\n--- ADDRESS ---")
        for selector in address_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"FOUND: {selector}")
                print(f"  Text: {elem.text}")
                print(f"  aria-label: {elem.get_attribute('aria-label')}")
                break
            except:
                print(f"NOT FOUND: {selector}")
        
        # Look for website
        website_selectors = [
            "a[data-item-id='authority']",
            "a[aria-label*='Website']",
            "[data-item-id='authority']"
        ]
        
        print("\n--- WEBSITE ---")
        for selector in website_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"FOUND: {selector}")
                print(f"  Text: {elem.text}")
                print(f"  href: {elem.get_attribute('href')}")
                break
            except:
                print(f"NOT FOUND: {selector}")
        
        # Look for category
        category_selectors = [
            "button.DkEaL",
            "button[jsaction*='category']",
            "[class*='DkEaL']"
        ]
        
        print("\n--- CATEGORY ---")
        for selector in category_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"FOUND: {selector}")
                print(f"  Text: {elem.text}")
                break
            except:
                print(f"NOT FOUND: {selector}")
        
        print("\n" + "="*60)
        print("Keeping browser open for 20 seconds for manual inspection...")
        print("="*60)
        time.sleep(20)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
    print("\nBrowser closed")
