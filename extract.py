from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import re

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)

#team codes tp iterate through
# states = ["Oregon","Arizona","California", "Colorado","Maryland","Nevada",
#   "New-Jersey","Utah","Washington", "New-York", "Nebraska",]
# abr = {
#     "Arizona": "AZ",
#     "California": "CA",
#     "Colorado": "CO",
#     "Maryland": "MD",
#     "Nevada": "NV",
#     "New-Jersey": "NJ",
#     "Oregon": "OR",
#     "Utah": "UT",
#     "Washington": "WA",
#     "New-York": "NY",
#     "Nebraska": "NE",

# }

states = [
    "California",
    "Connecticut",
    "Mississippi", "New-Jersey", "New-York", 
    "Oregon","Virginia",
]

abr = {
    "Alabama": "AL", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Illinois": "IL", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", 
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New-Hampshire": "NH", 
    "New-Jersey": "NJ", "New-Mexico": "NM", "New-York": "NY", "North-Carolina": "NC", 
    "North-Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", 
    "Pennsylvania": "PA", "Rhode-Island": "RI", "South-Carolina": "SC", "South-Dakota": "SD", 
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", 
    "Washington": "WA", "West-Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}




base_url = "https://www.nytimes.com/interactive/2024/11/05/us/elections/results-{}-president.html"

# Array to store data for each state
all_states_data = []
trump = 0
kamala = 0
otherVotes = 0

# Iterate over each state
for state in states:
    state_url = base_url.format(state.lower())
    driver.get(state_url)
    time.sleep(2)  # Adjust if necessary to allow page content to load
    
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    baseTrump = 'candidate-results-row-{}-G-P-2024-11-05-trump-d'
    trumpStateId = baseTrump.format(abr[state])

    baseKamala = 'candidate-results-row-{}-G-P-2024-11-05-harris-k'
    kamalaStateId = baseKamala.format(abr[state])
    other = 0

    print("STATE: " + state)
    # Get the data on how many votes other candidates have
    trumpRow = soup.find(id=trumpStateId)
    trumpStatePercent = float(trumpRow.find_all(class_='eln-17i7zw9')[1].get_text(strip=True)) / 100

    kamalaRow = soup.find(id=kamalaStateId)
    kamalaStatePercent = float(kamalaRow.find_all(class_='eln-17i7zw9')[1].get_text(strip=True)) / 100

    print(trumpStatePercent)
    print(kamalaStatePercent)
    other = 1 - kamalaStatePercent - trumpStatePercent
    print("Other percentage " + str(other))
    print("kamala + trump discounted percentage: " + str(0.5 - (other/2)))


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
                temp.append(0.5 - (other/2) + (num)/200)
                temp.append(0.5 - (other/2) - (num)/200)
            else:
                num = float(re.search(r'[-+]?\d*\.?\d+$', margin).group())
                temp.append(0.5 - (other/2) - (num)/200)
                temp.append(0.5 - (other/2) + (num)/200)

            #gets total vote in county
            temp.append(total)

            if percent == ">95%": 
                percent = 1
            else: 
                percent = (int)(percent[0:2]) / 100

            #gets percent of votes counted currently
            temp.append(percent)

        if len(temp) == 6:
            trump += temp[2] * (temp[4] / temp[5] - temp[4]) * 3
            kamala += temp[3] * (temp[4] / temp[5] - temp[4]) * 3
            otherVotes += other * (temp[4] / temp[5] - temp[4]) * 3
            all_states_data.append(temp)
            if temp[5] != 1: 
                print(temp)
            #print(temp)

driver.get('https://www.nytimes.com/interactive/2024/11/05/us/elections/results-president.html')
time.sleep(2)
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find the Democrat votes element
votesDem = soup.find(class_='footer-labels dem eln-1ljsxb2')
if votesDem:
    temp = votesDem.find(class_='all-votes-numbers eln-1ljsxb2').get_text(strip=True).replace(",", "").split(" ")
    kamalavotes = int(temp[0])

votesRep = soup.find(class_='footer-labels gop eln-1ljsxb2')
if votesRep:
    temp = votesRep.find(class_='all-votes-numbers eln-1ljsxb2').get_text(strip=True).replace(",", "").split(" ")
    trumpvotes = int(temp[0])
driver.quit()

print("------------------------")

print("Projected Trump Additional Votes:", trump)
print("Projected Kamala Additional Votes:", kamala)
print("Projected other Additional Votes:", otherVotes)
print("Percent Kamal: ", (kamala / (trump + kamala)))
projectedKamala = kamala + kamalavotes
projectedTrump = trump + trumpvotes
print("Projected Total Kamala Votes:", projectedKamala)
print("Projected Total Trump Votes:", projectedTrump)

print("------------------------")

print("CURRENT")
print("Current Votes for Kamala:", kamalavotes)
print("Current Votes for Trumo:", trumpvotes)
#UPDATE CONSTANTLY
allVotes = trumpvotes + kamalavotes + 773000 + 749000 + 639000 + 387000
print("Current Trump Percentage:", (trumpvotes)/(allVotes))
print("Current Kamala Percentage:", (kamalavotes) / (allVotes))
print("Current Margin:", (trumpvotes)/(allVotes) - (kamalavotes) / (allVotes))

print("------------------------")

print("PROJECTED WITH NYT TOTAL DATA")
#UPDATE CONSTANTLY
projectedTotal = allVotes / 0.995
print("Projected NYT Total: ", projectedTotal)
print("Projected NYT Trump Percent:", (projectedTrump/projectedTotal))
print("Projected NYT Kamala Percent:", (projectedKamala/projectedTotal))
print("Projected NYT other vote:", (1-(projectedTrump/projectedTotal) - (projectedKamala/projectedTotal)))
print("Projected NYT Margin:", (projectedTrump/projectedTotal) - (projectedKamala/projectedTotal))

print("------------------------")

print("PROJECTION WITHOUT NYT TOTAL DATA")
print("NO NYT Projected Total Votes:", (allVotes + kamala + trump + otherVotes))
print("No NYT Projected Trump Percent:", (projectedTrump/ (allVotes + kamala + trump + otherVotes)))
print("No NYT Projected Kamala Percent:", (projectedKamala/ (allVotes + kamala + trump + otherVotes)))
print("No NYT Projected Other Percent:", (1 - (projectedKamala/ (allVotes + kamala + trump + otherVotes)) - (projectedTrump/ (allVotes + kamala + trump + otherVotes))))
print("No NYT Projected Margin:", ((projectedTrump/ (allVotes + kamala + trump + otherVotes)) - (projectedKamala/ (allVotes + kamala + trump + otherVotes))))