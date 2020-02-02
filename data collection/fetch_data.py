from bs4 import BeautifulSoup
import json
import re 


player = open("collins.html", encoding="utf8")

def get_team_urls(teams):
    # Takes an opened html file as input, which should be from the page that lists all teams. Returns a list of team urls.

    soup = BeautifulSoup(teams.read(), 'html.parser')
    team_urls = soup.findAll("li", {"class": "list-group-item"})
    team_urls = [t.a.get("href") for t in team_urls]
    return team_urls

def team_url_to_name(url):
    return url.split("/")[0]

def get_player_urls(team):
    # Takes an opened html file as input, which should be from a team's page. Returns a list of player urls for the team

    soup = BeautifulSoup(team.read(), 'html.parser')
    player_urls = soup.findAll("td", {"class": "roster-entry"})
    player_urls = [p.a.get("href") for p in player_urls]
    return player_urls

def player_url_to_name(url):
    return url.split("/")[0]

def get_player_ratings(player):
    # Takes an opened html file as input, which should be from a player's page. Returns a dict that maps week number to player rating.

    soup = BeautifulSoup(player.read(), 'html.parser')
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
        pass

# print(get_player_urls(team))

team_url_to_name("https://nba2k19.2kratings.com/team/portland-trail-blazers")
