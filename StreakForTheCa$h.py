# -*- coding: utf-8 -*-
"""
Streak for the Ca$h Bot
Created on Wed Jun 01 21:48:11 2016

@author: Michael
"""

#### Libraries ####
import time
import urllib2
from bs4 import BeautifulSoup
from selenium import webdriver
#from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By
#from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import pandas as pd
from dateutil.parser import parse
import datetime

### open website and collect data to decide which pick to make ####
response = urllib2.urlopen("http://streak.espn.go.com/")
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
period = []
sports = []
for matchup in matchups:
    descs.append(matchup.find('div', {'class':'gamequestion'}).strong.getText())
    temps.append(matchup.find('div', {'class':'heatindex'}).getText())
    percs.append(float(matchup.find('span', {'class': 'wpw'}).getText()[0:len(matchup.find('span', {'class': 'wpw'}).getText())-1]))
    times.append(parse(matchup.find('span',{'class':'startTime'})['data-locktime'] ))
    if percs[len(percs)-1] < 50: # only keep the one with greater probabilty and record whether that was on the top or bottom
        percs[len(percs)-1] = 100-percs[len(percs)-1]
        topBottom.append("Bottom")
    else:
        topBottom.append("Top")
	if matchup.find('div', {'class':'sport-description'}) is not None:        
		sports.append(matchup.find('div', {'class':'sport-description'}).getText())
    else:
		sports.append("Unknown")
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
	period.append('Game') # Need to implement desc scanning
d = {"desc": descs, "time": times, "temp": temps, "perc": percs, 'topBottom': topBottom, 'selectionID': selectionIds, 'sport': sports, 'period': period}
data = pd.DataFrame(d)

# Load in the "durations" file and determine what period of time each matchup will take
duration = pd.read_csv("duration.csv")
data = pd.merge(data,duration, how='left', left_on = ['sport', 'period'], right_on = ['Sport','Period'])
data.set_value(data['Length'].isnull() ,'Length', 120) # for all NaN's that didn't merge in, give it a default of 2 hours
end_times = []
for length in data['Length']:
    end_times.append(data['time'] + (datetime.timedelta(minutes=length)))
data['end_time'] = end_times

# Determine matchups that overlap in time (if you pick one, you can't pick the other)
overlapMatchupsList = []
overlapMatchups = []
for i in range(0,len(data['time'])-1):
    overlapMatchups = []
    for j in range(0,len(data['time'])-1):
        if ( ( (data.iloc[j]['time'] >= data.iloc[i]['time'] 
            and data.iloc[j]['time'] <= data.iloc[i]['end_time'])
            or (data.iloc[j]['end_time'] >= data.iloc[i]['time'] and
            data.iloc[j]['end_time'] <= data.iloc[i]['end_time'])) and
           i != j):
                overlapMatchups.append(j)
    overlapMatchupsList.append(overlapMatchups)
data['overlapping'] = overlapMatchupsList

# Merge in win probabilities (these are going to come from StreakEdge).. but for now using perc


# Calculate expected wins of all possible remaining paths
possibleMatchups = data.loc[~data['selectionID'].isin(['unselectable'])]
possiblePaths = []
# if we were to do the power set (all possible subsets) of something around 20 matchups, it would be over 600,000 possible paths
# Method proposed: start with 1st event of the day, compare with all overlapping... move on to second and compare, etc...


# Get the element id of the one we want to choose
# right now the criteria is the soonest 90%+ pick that is not cold or none
pick = data.loc[ (~data['selectionID'].isin(["unselectable"])) & (data['perc'] > 80) & (~data['temp'].isin(['None']))]
#,'Cold']))]
pick = pick.ix[min(pick.index),'selectionID']

### Connect to website and click the link of soonest and/or hottest/ most likely pick ###

#Get the driver
chromedriver = "C:/Users/Michael/Downloads/chromedriver"
#binary = FirefoxBinary('C:/Program Files (x86)/Mozilla Firefox/firefox.exe')
driver = webdriver.Chrome(chromedriver) #.Firefox(firefox_binary = binary)

# Open the site
driver.get("http://streak.espn.go.com/")
## Click the desired pick
xpath = "//a[@selectionid='" + pick + "']"
elem = driver.find_element(By.XPATH,xpath)
elem.click()
## Collect new frames on the site (the log-in pop up)
frms = driver.find_elements_by_xpath("(//iframe[@id='disneyid-iframe'])")
#
## Switch to the log-in frame and log-in to save pick
driver.switch_to_frame(frms[0])
time.sleep(5)
driver.find_element_by_xpath("//input[@placeholder='Username or Email Address']").send_keys("******")
driver.find_element_by_xpath("//input[@placeholder='Password (case sensitive)']").send_keys("******")
driver.find_element_by_xpath("//button[@type='submit']").click()
time.sleep(7)
driver.close()