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
d = {"desc": descs, "time": times, "temp": temps, "perc": percs, 'topBottom': topBottom, 'selectionID': selectionIds}
data = pd.DataFrame(d)

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