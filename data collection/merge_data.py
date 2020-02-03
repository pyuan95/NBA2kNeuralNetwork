import pickle
file_names = ["2k18_player_names_only.p", "2k19_player_names_only.p", "2k20_player_names_only.p"]
data = dict()
for f in file_names:
    x = pickle.load(open(f, "rb"))
    for key in x:
        data[key] = x[key]
output = open("2k_player_names_only_merged.p", "wb")
pickle.dump(data, output)
