#-----------------------#
## Streak for the Cash ##
##     Strategieries   ##
##                     ##
##       M. Dickey     ##
#-----------------------#

## Libraries ##
library(ggplot2)
library(dplyr)
library(stringr)
library(scales)
library(png)
library(grid)

#Data
setwd("C:/Users/Michael/Documents/Side Projects/StreakForTheCash/")
Picks <- read.csv("StreakForTheCash/historicalPicks.csv", stringsAsFactors = F)

## Data manipulation ##
Picks$league <- substr(Picks$desc, 1, (regexpr(':', Picks$desc)-1)) # up to the colon is the league
Picks$league[which(regexpr('\\(', Picks$league) != -1 & Picks$league != "")] <- 
  substr(Picks$league[which(regexpr('\\(', Picks$league) != -1 & Picks$league != "")], 1,
         (regexpr('\\(', Picks$league[which(regexpr('\\(', Picks$league) != -1 & Picks$league != "")])-2)) # get rid of text before parentheses
Picks$winNum <- ifelse(Picks$win == "Yes", 1, 0) 
Picks$keyword <- if("WIN" %in% Picks$desc){"WIN"} else {gsub(" ", "", str_match(Picks$desc, " [^a-z]+[^:] "))}
Picks <- Picks[,-c(1,4)] #Extra columns
## Define Men's vs. Women's Tennis
Picks$sport[which(Picks$sport == "Tennis" & rownames(Picks) %in% grep("Men's", Picks$desc))] <- "Men's Tennis"
Picks$sport[which(Picks$sport == "Tennis" & rownames(Picks) %in% grep("Gentleman's", Picks$desc))] <- "Men's Tennis"
Picks$sport[which(Picks$sport == "Tennis" & rownames(Picks) %in% grep("Women's", Picks$desc))] <- "Women's Tennis" 
Picks$sport[which(Picks$sport == "Tennis" & rownames(Picks) %in% grep("Ladies", Picks$desc))] <- "Women's Tennis"

## Summary stats ####
mean(Picks$winNum) # ESPN does a pretty good job of keeping it around 50% overall

# What's the best sport to pick?
dat <- Picks %>% group_by(sport) %>% summarise(winPct=mean(winNum), count = n()) %>% filter(count > 200) %>% arrange(winPct)
dat$sport <- factor(dat$sport, levels = unique(dat$sport)) 
ggplot(data = dat, aes(x=sport, y = winPct)) +
  geom_bar(stat="identity") +
  coord_flip() + ggtitle("Winning %s of Popular Sports Picks")
# all seem to hover around .500 pretty well

# Look into relationship between confidence and win %
img <- readPNG("Images + Plots/SFTC.png")
g <- rasterGrob(img, interpolate=TRUE)
Picks$pctGroup <- as.numeric(cut_number(Picks$perc, 20))
Picks$pctGroup <- rescale(Picks$pctGroup, to = c(50, 100))
dat2 <- Picks %>% group_by(pctGroup) %>% summarise(winPct = mean(winNum), count = n()) %>% arrange(winPct)
ggplot(data = dat2, aes(x=pctGroup, y = winPct)) +
  geom_point(color = 'steelblue', size = 2) + labs(x = "Percent Choosing Favorite", y = "Win %") +
  annotation_custom(g, xmin = 50, xmax = 55, ymin = .525, ymax = .54) +
  ggtitle("Confidence != Winning")

# Split by hot-ness of pick
dat3 <- Picks %>% group_by(pctGroup, temp) %>% summarise(winPct = mean(winNum), count = n()) %>% filter(temp != "None") %>% arrange(winPct)
ggplot(data = dat3, aes(x=pctGroup, y = winPct)) +
  geom_point(color = 'steelblue', size = 2) + labs(x = "Percent Choosing Favorite", y = "Win %") +
  facet_grid(. ~ temp) +
  ggtitle("Confidence != Winning Across All Hotness")

# Split by sport of pick
dat4 <- Picks %>% group_by(pctGroup, sport) %>% summarise(winPct = mean(winNum), count = n()) %>% filter(count >10) %>% arrange(winPct)
ggplot(data = dat4, aes(x=pctGroup, y = winPct)) +
  geom_point(color = 'steelblue', size = 2) + labs(x = "Percent Choosing Favorite", y = "Win %") +
  facet_grid(. ~ sport) +
  ggtitle("Confidence != Winning Across All Hotness")



## With this in mind... Maybe we should be trying to optimize # of wins per month rather than going for a streak?
# (thinking that streaks may have more advanced strategy like knowing when to refrain from picking)

# Create approximate durations data (to ensure the most picks/day)
Duration <- Picks %>% group_by(sport, keyword) %>% summarise(count = n()) %>% filter(count > 10)
Duration$duration <- 120 # 2 hours by default
Duration$duration[which(Duration$sport == "Tennis")] <- 2.75*60 # 2.75 for ambiguous tennis
Duration$duration[which(Duration$sport == "Men's Tennis")] <- 3.5*60 
Duration$duration[which(Duration$sport == "Women's Tennis")] <- 120
Duration$duration[which(Duration$sport == "NCB" & Duration$keyword %in% c("GAME", "WIN"))] <-  120
