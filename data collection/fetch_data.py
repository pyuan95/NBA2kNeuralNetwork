from bs4 import BeautifulSoup
import json
import re 
from urllib.request import urlopen, Request, urlretrieve

# player = open("towns.html", encoding="utf8")

def get_team_urls(teams):
    # Takes an opened html file as input, which should be from the page that lists all teams. Returns a list of team urls.

    soup = BeautifulSoup(teams, 'html.parser')
    team_urls = soup.findAll("li", {"class": "list-group-item"})
    team_urls = [t.a.get("href") for t in team_urls]
    return team_urls

def team_url_to_name(url):
    return url.split("/")[-1]

def get_player_urls(team):
    # Takes an opened html file as input, which should be from a team's page. Returns a list of player urls for the team

    soup = BeautifulSoup(team, 'html.parser')
    player_urls = soup.findAll("td", {"class": "roster-entry"})
    player_urls = [p.a.get("href") for p in player_urls]
    return player_urls

def player_url_to_name(url):
    return url.split("/")[0]

def get_player_number(player):
    # Takes an opened html file as input, which should be from a player's page. Returns a dict that maps week number to player rating.
    soup = BeautifulSoup(player, 'html.parser')
    player_num = soup.findAll("h2", {"class": "player-jersey"})[0]
    player_num = player_num.string
    player_num = player_num[player_num.index("#") + 1:player_num.index("|")]
    return int(player_num)

def download_webpage(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}
    req = Request(url=url, headers=headers) 
    html = urlopen(req)
    content =  html.read().decode(html.headers.get_content_charset())
    return content

def get_player_ratings(player):
    # Takes an opened html file as input, which should be from a player's page. Returns a dict that maps week number to player rating.

    soup = BeautifulSoup(player, 'html.parser')
    ratings = soup.findAll("script")
    ratings = [p.string for p in ratings if "new Chartist.Line" in str(p)]
    ratings = ratings[0]
    ratings = ratings[ratings.index("[[") + 2:ratings.index("]]")]
    ratings = ratings.strip().split("\n")
    ratings = [re.sub("\t", "", r).strip() for r in ratings]
    ratings = [re.sub("},", "}", r) for r in ratings]
    weeks = [int(r[r.index("x:") + 3: r.index(",")]) for r in ratings]
    nums = [int(r[r.index("y:") + 3: r.index("}")]) for r in ratings]
    ratings_zipped = list(zip(weeks, nums))
    ratings = dict()
    for r in ratings_zipped:
        ratings[r[0]] = r[1]
    return ratings

def dump_to_json(teams, year):
    # Takes an opened html file as input, which should be from the page that lists all the teams.
    # returns a json file in the following format:
    #
    # year
	#   team
	# 	    player number
	# 		    player name
	# 		    ratings

    data = dict()
    data[year] = dict()
    team_urls = get_team_urls(teams)
    for team in team_urls:
        team_urls = get_team_urls(team)
        for team_url in team_urls:
            pass


# print(get_player_urls(team))

player = download_webpage("https://www.2kratings.com/nba2k20/karl-anthony-towns")
print(get_player_number(player))
print(get_player_ratings(player))
