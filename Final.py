import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def scrape_data(url):
    web = 'https://www.bytestobytes.com/w/' + url
    driver = webdriver.Chrome()
    driver.get(web)

    # Wait for the dynamically loaded content to appear
    wait = WebDriverWait(driver, 5)

    # Define a regular expression pattern for currency values
    bytes_pattern = re.compile(r'\d+')
    currency_pattern = re.compile(r'\$\d+(?:,\d{3})*(?:\.\d{2})?')
    currency_pattern_2 = re.compile(r'\d+(?:\.\d+)?')

    # XPath selectors
    xpath_bytes = '//h2[contains(@class, "font-bold text-xl")]/span'
    xpath_selector_1 = '//span[@class=""]'
    xpath_selector_2 = '//span[@class=""][contains(text(), "Ξ")]'
    xpath_selector_3 = '(//span[@class=""])[3]'  # Modified selector for third item
    xpath_square_button = '//button[contains(@class, "rounded-xl border overflow-hidden relative shadow-lg")]'
    # XPath AFTER CLICK
    xpath_citizen_number = '//h3[contains(@class, "text-foreground")][starts-with(text(), "Citizen #")]'
    xpath_time_lock = '//div[@class="flex items-center space-x-2"]/span[contains(text(), "months") or contains(text(), "month")]'
    xpath_stake_bytes = '//div[@class="flex items-center space-x-2"]/span'

    # Find the square button element and click it
    square_button = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_square_button)))
    square_button.click()

    # Wait for the new content to load
    time.sleep(3)

    # Find all <span> elements
    span_bytes = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_bytes)))
    span_elements_1 = wait.until(EC.visibility_of_all_elements_located((By.XPATH, xpath_selector_1)))
    span_elements_2 = wait.until(EC.visibility_of_all_elements_located((By.XPATH, xpath_selector_2)))
    span_elements_3 = wait.until(EC.visibility_of_all_elements_located((By.XPATH, xpath_selector_3)))
    #AFTER CLICK
    citizen_number_element = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_citizen_number)))
    time_lock_element_div = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_time_lock)))
    stake_bytes_elements = wait.until(EC.visibility_of_all_elements_located((By.XPATH, xpath_stake_bytes)))

    # Extract and print the currency values using the regular expression
    citizen_number_text = citizen_number_element.text
    citizen_number = citizen_number_text.replace("Citizen #", "").strip()
    time_lock = time_lock_element_div.text.strip()

    for element in stake_bytes_elements:
        # Filter out elements "unclaimed BYTES"
        if element.text.strip().isdigit():
            stake_bytes = element.text.strip()
            break
    #______________________________________________

    match = bytes_pattern.search(span_bytes.text)
    if match:
        bites = match.group()
        print(match.group())
        
    for span in span_elements_1:
        match = currency_pattern.search(span.text)
        if match:
            print(match.group())

    # (Ξ value)
    for span in span_elements_2:
        print(span.text)

    # third value
    for span in span_elements_3:
        match = currency_pattern_2.search(span.text)
        if match:
            print(match.group())

    print(" ")
    print("Citizen Number:", citizen_number)
    print("Time Lock:", time_lock)
    print("Stake Bytes:", stake_bytes)

    data_test = {
        'USD Earnings': span_elements_1[0].text,
        'ETH Earnings': span_elements_2[0].text,
        'Bytes in Wallet': span_elements_3[0].text,
        'Unclaimed Bytes': bites,
        'S1 Citizens': citizen_number,
        'Bytes Staked': stake_bytes,
        'Time Lock': time_lock
}   
    # Close the browser and return extracted stuff
    driver.quit()
    return data_test


scraped_data = []
df = pd.read_excel('NT.xlsx')

# Iterate through the URLs and final format data
for index, row in df.iterrows():
    url = row['Address']
    try:
        data = scrape_data(url)
        data['USD Earnings'] = float(re.sub(r'[^\d.]', '', data['USD Earnings']))
        data['ETH Earnings'] = float(data['ETH Earnings'].replace('Ξ ', ''))
        data['Bytes in Wallet'] = float(data['Bytes in Wallet'])
        data['Unclaimed Bytes'] = int(data['Unclaimed Bytes'])
        data['S1 Citizens'] = int(data['S1 Citizens'])
        data['Bytes Staked'] = int(data['Bytes Staked'])
        scraped_data.append(data)
    except Exception as e:
        print(f"Error scraping data for URL {url}: {e}")
        
    if index == 4:
        break

result_df = pd.DataFrame(scraped_data)
# Write the DataFrame to Excel file
result_df.to_excel('scraped_example.xlsx', index=False)