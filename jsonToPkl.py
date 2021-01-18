import json
import os
import pickle

grenades = {}
directory = r'maps/'
for filename in os.listdir(directory):
    mapa = filename.split('.')[0]
    f = open(directory + filename, encoding='utf-8')
    data = json.load(f)
    grenades[mapa] = sorted(data['pageProps']['ssrNades'], key = lambda i: i['favoriteCount'], reverse=True)

file = open('grenades.pkl', 'wb')
pickle.dump(grenades, file)
file.close()