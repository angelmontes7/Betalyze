"""
Install
pip install cloudscraper
pip install beautifulsoup4
pip install pandas
pip install lxml html5lib
"""

# IF IT SAYS TABLE IS NOT FOUND THEN YOU HAVE BEEN BLOCKED OR REACHED RATE LIMIT (increase sleep time)

# Imports
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time
import random


def scraping_one_team():
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
    soup = BeautifulSoup(data.text, "html.parser") # parse the content

    links = soup.find_all('a') # find all links on the page
    links = [l.get("href") for l in links] # get the url
    links = [l for l in links if l and 'all_comps/shooting/' in l] # get specific url that relates to the shooting stats

    data = scraper.get(f"https://fbref.com{links[0]}") # download data from link
    shooting = pd.read_html(data.text, match="Shooting")[0] # Finds the specific string "Shooting"
    shooting.columns = shooting.columns.droplevel() # Pandas dataframe is multi-level index therefore we need to drop one index level

    team_data = matches[0].merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date") # merge the matches and shooting dataframes into one

    print(team_data.head()) # Display data frame


def scraping_all_teams():
    scraper = cloudscraper.create_scraper() #Create scrapper
    standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats" # Website URL

    years = list(range(2025, 2020, -1)) # The years we will be scrapping from
    all_matches = []

    # Loops through all the wanted years
    for year in years:
        data = scraper.get(standings_url)
        soup = BeautifulSoup(data.text, "html.parser")
        standings_table = soup.select_one('table.stats_table')

        # Gets each teams url
        links = [l.get("href") for l in standings_table.find_all('a')]
        links = [l for l in links if '/squads/' in l]
        team_urls = [f"https://fbref.com{l}" for l in links]
        print(f"[{year}] Gathered team URLs: {len(team_urls)} teams")

        # Gets the previous season
        previous_season = soup.select("a.prev")[0].get("href")
        standings_url = f"https://fbref.com/{previous_season}"
        
        # Loops through each teams url to get corresponding data
        for team_url in team_urls:
            team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ") # removes stats and - from team name
            print(f"[{year}] Starting on: {team_name}")

            # Gathers data regarding the teams Scores and fixtures
            data = scraper.get(team_url)
            matches = pd.read_html(data.text, match="Scores & Fixtures")[0]

            # Gets shooting data
            soup = BeautifulSoup(data.text, "html.parser")
            links = [l.get("href") for l in soup.find_all('a')]
            links = [l for l in links if l and 'all_comps/shooting/' in l]
            data = scraper.get(f"https://fbref.com{links[0]}")
            shooting = pd.read_html(data.text, match="Shooting")[0]
            shooting.columns = shooting.columns.droplevel()

            try:
                team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date") #merge shooting stats with match stats
            except ValueError:
                continue
            
            team_data = team_data[team_data["Comp"] == "Premier League"] # Filters for only games in the premier league

            # Adding columns for organization purposes
            team_data["Season"] = year
            team_data["Team"] = team_name

            all_matches.append(team_data) # Appending changes

            time.sleep(random.uniform(7, 15)) # Sleep to try and not get blocked by cloudflare

        # Sleep after finishing one season
        print(f"[{year}] Finished season — sleeping before next year...")
        time.sleep(random.uniform(15, 30))

    match_df = pd.concat(all_matches) # Create pandas dataframe
    match_df.columns = [c.lower() for c in match_df.columns] # convert everything to lowercase

    print("Finally creating .csv file!!")
    match_df.to_csv("matches.csv") # Create a .csv file
    print("matches.csv saved successfully.")



def main():
    scraping_all_teams()

if __name__ == "__main__":
    main()
