__author__ = 'meraj'
from subprocess import call
import os
import urllib, json
import requests

files = os.listdir('data/positionlog')
for file in files:
    url = 'http://stats.nba.com/stats/playbyplayv2'
    options ={'EndPeriod':10, 'EndRange': 55800, 'GameID':file[:-5], 'RangeType':2, 'Season:' '2015-16' 'SeasonType': 'Regular+Season', 'StartPeriod':1, 'StartRange':0}
    print(requests.get(url, options))