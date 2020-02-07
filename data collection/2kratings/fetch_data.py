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
    return re.sub("-","_",url.split("/")[-1])

def get_player_urls(team):
    # Takes an opened html file as input, which should be from a team's page. Returns a list of player urls for the team

    soup = BeautifulSoup(team, 'html.parser')
    player_urls = soup.findAll("td", {"class": "roster-entry"})
    player_urls = [p.a.get("href") for p in player_urls]
    return player_urls

def player_url_to_name(url):
    return re.sub("-","_",url.split("/")[-1])

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
    try:
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
    except:
        # Player has no week by week ratings. Get the default rating and package it in week by week format
        soup = BeautifulSoup(player, 'html.parser')
        ratings = soup.findAll("div", {"class": "container-fluid player-content"})[0]
        ratings = ratings.div.div.contents[0]
        print(ratings)
        rating = int(ratings)
        ratings = dict()
        for i in range(30):
            ratings[i] = rating
        return ratings

def dump_data(teams, year):
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

    failed_players = []

    team_urls = get_team_urls(teams)
    # change team urls for 2017 and 2018
    team_urls = ['https://nba2k19.2kratings.com/team/atlanta-hawks', 'https://nba2k19.2kratings.com/team/boston-celtics', 'https://nba2k19.2kratings.com/team/brooklyn-nets', 'https://nba2k19.2kratings.com/team/charlotte-hornets', 'https://nba2k19.2kratings.com/team/chicago-bulls', 'https://nba2k19.2kratings.com/team/cleveland-cavaliers', 'https://nba2k19.2kratings.com/team/dallas-mavericks', 'https://nba2k19.2kratings.com/team/denver-nuggets', 'https://nba2k19.2kratings.com/team/detroit-pistons', 'https://nba2k19.2kratings.com/team/golden-state-warriors', 'https://nba2k19.2kratings.com/team/houston-rockets', 'https://nba2k19.2kratings.com/team/indiana-pacers', 'https://nba2k19.2kratings.com/team/los-angeles-clippers', 'https://nba2k19.2kratings.com/team/los-angeles-lakers', 'https://nba2k19.2kratings.com/team/memphis-grizzlies', 'https://nba2k19.2kratings.com/team/miami-heat', 'https://nba2k19.2kratings.com/team/milwaukee-bucks', 'https://nba2k19.2kratings.com/team/minnesota-timberwolves', 'https://nba2k19.2kratings.com/team/new-orleans-pelicans', 'https://nba2k19.2kratings.com/team/new-york-knicks', 'https://nba2k19.2kratings.com/team/oklahoma-city-thunder', 'https://nba2k19.2kratings.com/team/orlando-magic', 'https://nba2k19.2kratings.com/team/philadelphia-76ers', 'https://nba2k19.2kratings.com/team/phoenix-suns', 'https://nba2k19.2kratings.com/team/portland-trail-blazers', 'https://nba2k19.2kratings.com/team/sacramento-kings', 'https://nba2k19.2kratings.com/team/san-antonio-spurs', 'https://nba2k19.2kratings.com/team/utah-jazz', 'https://nba2k19.2kratings.com/team/toronto-raptors', 'https://nba2k19.2kratings.com/team/washington-wizards']
    team_urls = [re.sub("nba2k19", "nba2k18", t) for t in team_urls]
    for team_url in team_urls:
        print(team_url)
        if team_url == "https://nba2k19.2kratings.com/team/boston-celtics":
            # break
            pass
        team = download_webpage(team_url)
        team_name = team_url_to_name(team_url)
        data[year][team_name] = dict()
        player_urls = get_player_urls(team)
        print("TEAM: ", team_name)
        for player_url in player_urls:
            player = download_webpage(player_url)
            player_name = player_url_to_name(player_url)
            print("\tPLAYER: ", player_name)
            try:
                player_num = get_player_number(player)
                player_ratings = get_player_ratings(player)
                data[year][team_name][player_name] = dict()
                data[year][team_name][player_name]["player_number"] = player_num
                data[year][team_name][player_num]["player_ratings"] = player_ratings
                data_player_names_only[year][player_name] = dict()
                data_player_names_only[year][player_name]["player_number"] = player_num
                data_player_names_only[year][player_name]["player_ratings"] = player_ratings
            except Exception as e:
                failed_players.append(player_name)
                print(e)

    log = open("log_failed" + str(year), "w")
    log.write(str(failed_players))
    log.close()
    print("FAILED PLAYERS: ", failed_players)
    return data, data_player_names_only

if __name__ == "__main__":
    teams_2018 = download_webpage("https://nba2k19.2kratings.com/current-teams-on-nba-2k19")
    data, data_player_names_only = dump_data(teams_2018, 2017)

    output = open("2k17.p", "wb")
    pickle.dump(data, output, protocol=pickle.HIGHEST_PROTOCOL)
    output.close()

    output = open("2k17_player_names_only.p", "wb")
    pickle.dump(data_player_names_only, output)
    output.close()

# player = download_webpage("https://www.2kratings.com/nba2k20/vince-carter")
# print(get_player_ratings(player))

