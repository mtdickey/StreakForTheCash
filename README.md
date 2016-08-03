# StreakForTheCash
Automatic selection of SFTC matchups with Python Data Scraping/Analysis

The primary goal of this project is to create an automated program with an impeccable ability to pick the sports matchups posed daily on ESPN's Streak for the Cash competition ([Streak.ESPN.com](https://www.streak.espn.com)).

- - - -

__About SFTC__:
In this free competition, users may win cash prizes up to $25,000 by either:

1. Having the longest streak of correct picks out of all players for the month
2. Accumulating the maxmimum number of correct picks for the month

There are a variety of matchups that players may choose from, spanning all common sports:
* Picking the winning team/player (this is the most common pick)
* Picking the winning "side" of a prop bet, which may only last a brief portion of the game
  * (Ex. Which QB will have more yards in the first half?)

__Rules__:
* Players may not register multiple accounts
* Only 1 pick may be made at a time
* __Note:__ A player may "forfeit" their pick if they wish to make another selection before their current matchup ends

- - - -
__Objectives of the project:__

1. __Identify a winning strategy:__ Develop two programs with objectives matching the two ways to way, listed above
2. __Utilize the best information available__, including:
  1. Other SFTC analytics sites (Ex. [Streak Edge](https://www.streakege.com))
  2. Live monitoring of ongoing picks
  3. Betting lines/Sports analytics sites publishing predictions (Ex. [538](http://fivethirtyeight.com/sports/))
  4. *Stretch*: Internal modeling/simulations
3. __Identify patterns of favorable matchups__

__Challenges:__

1. __Text analytics:__ Translating the matchup text posed into the period of time that the matchup will be active
2. __Optimization:__ Maximize expected wins given estimates of win probabilities and the number of picks possible
3. __Classification:__ Separating the winners from the losers
4. __Real Time:__ Monitoring on-going matchups to get a better estimate of live win probabilties
