"""
Debug script to inspect Google Maps HTML structure
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
    query = "dentist in boston"
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
        
        print("\n" + "="*60)
        print("INSPECTING FIRST BUSINESS ELEMENT")
        print("="*60)
        
        # Get the outer HTML
        outer_html = element.get_attribute('outerHTML')
        
        # Save to file for inspection
        with open('debug_element.html', 'w', encoding='utf-8') as f:
            f.write(outer_html)
        
        print("\n✓ Saved HTML to debug_element.html")
        
        # Try to find the link
        try:
            link = element.find_element(By.CSS_SELECTOR, "a.hfpxzc")
            print("\n✓ Found link with class 'hfpxzc'")
            print(f"  aria-label: {link.get_attribute('aria-label')}")
            
            # Get all child elements
            children = link.find_elements(By.XPATH, ".//*")
            print(f"\n  Link has {len(children)} child elements:")
            
            for i, child in enumerate(children[:10]):  # First 10 only
                tag = child.tag_name
                classes = child.get_attribute('class')
                text = child.text[:50] if child.text else ''
                print(f"    [{i}] <{tag}> class='{classes}' text='{text}'")
        except Exception as e:
            print(f"\n✗ Error finding link: {e}")
        
        # Try different selectors
        selectors_to_try = [
            "div.fontHeadlineSmall",
            "div.qBF1Pd",
            "div.NrDZNb",
            "div.fontBodyMedium",
            "span.fontHeadlineSmall",
            "a.hfpxzc div:first-child",
        ]
        
        print("\n" + "="*60)
        print("TRYING DIFFERENT SELECTORS")
        print("="*60)
        
        for selector in selectors_to_try:
            try:
                elem = element.find_element(By.CSS_SELECTOR, selector)
                print(f"\n✓ {selector}")
                print(f"  Text: '{elem.text}'")
                print(f"  Class: '{elem.get_attribute('class')}'")
            except:
                print(f"\n✗ {selector} - NOT FOUND")
        
        print("\n" + "="*60)
        print("Keeping browser open for 30 seconds for manual inspection...")
        print("="*60)
        time.sleep(30)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
    print("\nBrowser closed")
