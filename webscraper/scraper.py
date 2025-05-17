"""
Install
pip install cloudscraper
pip install BeautifulSoup
pip install pandas
"""

# IF IT SAYS TABLE IS NOT FOUND THEN YOU HAVE BEEN BLOCKED OR REACHED RATE LIMIT (increase sleep time)

# Imports
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import random


def scrapping_one_team():
    scraper = cloudscraper.create_scraper() #Create scrapper
    url = "https://fbref.com/en/comps/9/Premier-League-Stats" # Website URL
    response = scraper.get(url) # everything the scraper gathered

    soup = BeautifulSoup(response.text, "html.parser") # parses the content
    standings_table = soup.select_one('table.stats_table') # gets the stats_table

    # If there is a standing_table in the html content then find all a tags and get the links and filter to only get squad links
    if standings_table:
        links = standings_table.find_all('a')
        links = [l.get("href") for l in links if l.get("href") and '/squads/' in l.get("href")]
        print(links)
    else:
        print("Stats table not found.")
    
    team_urls = [f"https://fbref.com{l}" for l in links] # turn links into full url's


    team_url = team_urls[0] # use the first team url (liverpool for the 2024-2025 season)
    data = scraper.get(team_url) # Gets the html for that teams url
    matches = pd.read_html(data.text, match="Scores & Fixtures") # Finds the specific string "Score & Fixtures"
    soup = BeautifulSoup(data.text) # parse the content

    links = soup.find_all('a') # find all links on the page
    links = [l.get("href") for l in links] # get the url
    links = [l for l in links if l and 'all_comps/shooting/' in l] # get specific url that relates to the shooting stats

    data = scraper.get(f"https://fbref.com{links[0]}") # download data from link
    shooting = pd.read_html(data.text, match="Shooting")[0] # Finds the specific string "Shooting"
    shooting.columns = shooting.columns.droplevel() # Pandas dataframe is multi-level index therefore we need to drop one index level

    team_data = matches[0].merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date") # merge the matches and shooting dataframes into one

    print(team_data.head()) # Display data frame

def main():
    scrapping_one_team()

if __name__ == "__main__":
    main()
