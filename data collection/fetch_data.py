from bs4 import BeautifulSoup
import re 
from urllib.request import urlopen, Request, urlretrieve
import pickle 

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
    return url.split("/")[-1]

def get_player_number(player):
    # Takes an opened html file as input, which should be from a player's page. Returns a dict that maps week number to player rating.
    soup = BeautifulSoup(player, 'html.parser')
    player_num = soup.findAll("h2", {"class": "player-jersey"})[0]
    player_num = str(player_num)
    player_num = player_num[player_num.index("#") + 1:player_num.index("|")]
    # print(player_num)
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
    # returns a dict in the following format:
    #
    # year
	#   team
	# 	    player number
	# 		    player name
	# 		    ratings
    # It also returns a dict in the following format
    # year
    #   player_name
    #       player_num
    #       ratings

    data = dict()
    data[year] = dict()
    data_player_names_only = dict()
    data_player_names_only[year] = dict()

    team_urls = get_team_urls(teams)
    for team_url in team_urls:
        if team_url == "https://nba2k19.2kratings.com/team/boston-celtics":
            break
            # pass
        try:
            team = download_webpage(team_url)
            team_name = team_url_to_name(team_url)
            data[year][team_name] = dict()
            player_urls = get_player_urls(team)
            print("TEAM: ", team_name)
            for player_url in player_urls:
                player = download_webpage(player_url)
                player_name = player_url_to_name(player_url)
                print("PLAYER: ", player_name)
                player_num = get_player_number(player)
                player_ratings = get_player_ratings(player)
                data[year][team_name][player_num] = dict()
                data[year][team_name][player_num]["player_name"] = player_name
                data[year][team_name][player_num]["player_ratings"] = player_ratings
                data_player_names_only[year][player_name] = dict()
                data_player_names_only[year][player_name]["player_number"] = player_num
                data_player_names_only[year][player_name]["player_ratings"] = player_ratings
        except Exception as e:
            print(e)
    return data, data_player_names_only


# print(get_player_urls(team))
# player = download_webpage("https://nba2k19.2kratings.com/player/kyrie-irving")
# print(get_player_number(player))
if __name__ == "__main__":
    teams = download_webpage("https://nba2k19.2kratings.com/current-teams-on-nba-2k19")
    data, data_player_names_only = dump_to_json(teams, 2019)

    output = open("2k19.p", "wb")
    pickle.dump(data, output, protocol=pickle.HIGHEST_PROTOCOL)
    output.close()

    output = open("2k19_player_names_only.p", "wb")
    pickle.dump(data_player_names_only, output)
    output.close()


