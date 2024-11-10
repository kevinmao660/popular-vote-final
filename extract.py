from selenium import webdriver
from selenium.webdriver.common.by import By
import pprint
import json
from statistics import mean
import time
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import re

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)

#team codes tp iterate through
states = ["Arizona","California", "Colorado","Maryland","Nevada",
  "New Jersey","Oregon","Utah","Washington"
]

base_url = "https://www.nytimes.com/interactive/2024/11/05/us/elections/results-{}-president.html"

# Array to store data for each state
all_states_data = []
trump = 0
kamala = 0

# Iterate over each state
for state in states:
    state_url = base_url.format(state.lower())
    driver.get(state_url)
    time.sleep(2)  # Adjust if necessary to allow page content to load
    
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    elements = soup.find_all(class_='eln-d65730')

    actions = ActionChains(driver)
    actions.move_to_element(driver.find_element(By.TAG_NAME, "body")).perform()
    time.sleep(2)

    for element in elements:
        temp = []
        row_header = element.find(class_='black middle name row-header eln-z5gmhw')
        margin = element.find(class_='gray middle margin row-cell eln-z5gmhw')
        total = element.find(class_='right black middle total-votes row-cell eln-z5gmhw')
        percent = element.find(class_='right gray middle eevp row-cell eln-z5gmhw')

        if row_header and margin and total and percent:
            row_header = row_header.get_text(strip=True)
            margin = margin.get_text(strip=True)
            total = (int)(total.get_text(strip=True).replace(",", ""))
            percent = percent.get_text(strip=True)
            #gets county
            temp.append(row_header)

            #gets margin and puts trump percentage first kamala second
            temp.append(margin)
            if margin[0] == "T":
                num = float(re.search(r'[-+]?\d*\.?\d+$', margin).group())
                temp.append(0.495 + (num)/200)
                temp.append(0.495 - (num)/200)
            else:
                temp.append(0.495 - (num)/200)
                temp.append(0.495 + (num)/200)

            #gets total vote in county
            temp.append(total)

            if percent == ">95%": 
                percent = 1
                break
            else: 
                percent = (int)(percent[0:2]) / 100

            #gets percent of votes counted currently
            temp.append(percent)

        if len(temp) == 6:
            trump += temp[2] * temp[4] * (1-temp[5])
            kamala += temp[3] * temp[4] * (1-temp[5])
            all_states_data.append(temp)
            print(temp)

driver.quit()
print(trump)
print(kamala)