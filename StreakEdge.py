# -*- coding: utf-8 -*-
"""
Streak Edge Scraper
Created on Sun Jul 31 16:55:10 2016

Gather analysis from StreakEdge to collect a daily file with a comparison of all picks and estimated win probs

@author: Michael
"""


# Libraries # 
import urllib2
from bs4 import BeautifulSoup
import pandas as pd
from dateutil.parser import parse
import datetime

# open website and collect data to decide which pick to make #
link = 'http://www.streakedge.com/sftc-todays-picks/'
response = urllib2.urlopen(base+date)
html = response.read()
soup = BeautifulSoup(html)
    
#Get the matchups
matchups = soup.find_all('div', {'class': 'matchup-container'})
# Go through matchups and collect data (time, hot/cold, user pick %'s)
descs = [] # these should match the questions posed by SFTC (but some may duplicate and be at the same time, so we'll need to add team names
confidence = []
selection = []
winProb = []
for matchup in matchups:
	print("TBD")

d = {'desc': descs, 'confidence': confidence, 'selection': selection, 'winProb': winProb}
data =  pd.DataFrame(d)
	
data.to_csv("currentWinProbs.csv")
