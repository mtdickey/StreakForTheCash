# -*- coding: utf-8 -*-
"""
SFTC Scraper and Analysis
Created on Sun Jul 31 16:55:10 2016

Scrape historical picks and create a picking algorithm/strategy

@author: Michael
"""


#### Libraries ####
import urllib2
from bs4 import BeautifulSoup
import pandas as pd
from dateutil.parser import parse
import datetime

## Get a list of 600 dates to iterate through websites of
stamps = pd.date_range(pd.datetime.today() - datetime.timedelta(days=600), periods=600).tolist()
dates = [str(stamp.year) + str(stamp.month).zfill(2) + str(stamp.day).zfill(2) for stamp in stamps]

### open website and collect data to decide which pick to make ####
base = "http://streak.espn.go.com/en/entry?date="
data = pd.DataFrame(columns = ["desc", "time", "temp", "perc", 'topBottom', 'selectionID', 'sport', 'win'])
for date in dates:
    response = urllib2.urlopen(base+date)
    print(date)
    html = response.read()
    soup = BeautifulSoup(html)
    
    #Get the matchups
    matchups = soup.find_all('div', {'class': 'matchup-container'})
    # Go through matchups and collect data (time, hot/cold, user pick %'s)
    descs = []
    times = []
    temps = []
    percs = []
    topBottom = []
    selectionIds = []
    sports = []
    winTag = []
    win = []
    for matchup in matchups:
        if matchup.find('div', {'class':'gamequestion'}) is not None:
            descs.append(matchup.find('div', {'class':'gamequestion'}).strong.getText())
        else: ### Note: There are currently only 28 of these... but the questions were in different tags as matchups of the day ("<div class="spons-bgGame">")
            descs.append("Unknown")
        temps.append(matchup.find('div', {'class':'heatindex'}).getText())
        percs.append(float(matchup.find('span', {'class': 'wpw'}).getText()[0:len(matchup.find('span', {'class': 'wpw'}).getText())-1]))
        times.append(parse(matchup.find('span',{'class':'startTime'})['data-locktime'] ))
        if matchup.find('div', {'class':'sport-description'}) is not None:        
            sports.append(matchup.find('div', {'class':'sport-description'}).getText())
        else:
            sports.append("Unknown")
        if percs[len(percs)-1] < 50: # only keep the one with greater probabilty and record whether that was on the top or bottom
            percs[len(percs)-1] = 100-percs[len(percs)-1]
            topBottom.append("Bottom")
        else:
            topBottom.append("Top")
        # Now that we know if it's on top or bottom, find the selection id of the link that goes with that (so we can select it later)
        if topBottom[len(topBottom)-1] == "Top":
            if matchup.find('a', {'class': 'mg-check mg-checkEmpty requireLogin'}) is not None:
                selectionIds.append(matchup.find('a', {'class': 'mg-check mg-checkEmpty requireLogin'})['selectionid'])
            else:
                selectionIds.append("unselectable")
        else:
            if matchup.find('a', {'class': 'mg-check mg-checkEmpty requireLogin'}) is not None:
                selectionIds.append(matchup.find_all('a', {'class': 'mg-check mg-checkEmpty requireLogin'})[1]['selectionid'])
            else:
                selectionIds.append("unselectable")
        winTag.append(matchup.find('span', {'class': 'winner'}).getText())
        if 'arrow' in winTag[len(winTag)-1] and topBottom[len(topBottom)-1] == "Top":
            win.append("Yes")
        elif 'arrow' in winTag[len(winTag)-1] and topBottom[len(topBottom)-1] == "Bottom":
            win.append("No")
        elif 'arrow' not in winTag[len(winTag)-1] and topBottom[len(topBottom)-1] == "Top":
            win.append("No")
        elif 'arrow' not in winTag[len(winTag)-1] and topBottom[len(topBottom)-1] == "Bottom":
            win.append("Yes")
            
            
    d = {"desc": descs, "time": times, "temp": temps, "perc": percs, 'topBottom': topBottom, 'selectionID': selectionIds, 'sport': sports, 'win': win}
    data2 = pd.DataFrame(d)
    data = data.append(data2)

data.to_csv("historicalPicks.csv")
