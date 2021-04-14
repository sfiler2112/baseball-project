from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn import datasets
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pip._vendor.requests as requests
import pip._vendor.urllib3 as urllib3  # Used for exception handling
import os
import sys  # Used for exception handling
import ssl  # Used for exception handling 
import socket  # Used for exception handling
import logging
import re


logger = logging.Logger('catch_all')

def checkSeason(year):
	if year > 2020 or year < 1967:
		print("BAD YEAR!!!")
		return False
	return True

# Checks if the data-stat of a table cell currently being processed in getSeasonStatsCY is one that requires being cast as a float.
# Those data-stats are 'points_won', 'votes_first', 'WAR_pitch', 'win_loss_perc', 'earned_run_avg', 'IP', and 'whip'.
# Also check for the 'share' stat, which needs to have the percentage symbol removed and returned as an int.  
# 'name' and 'team_ID remain strings.
# All other stats are cast and returned as ints.
def evaluateStatType(statType, statValue):
	if statType == 'name' or statType == 'team_ID':
		print(statValue)
		return statValue
	elif statType == 'share':
		return int(statValue[0:len(statValue) - 1])
	elif statType == 'points_won' or statType == 'votes_first' or statType == 'WAR_pitch' or statType == 'win_loss_perc' or statType == 'earned_run_avg' or 'IP' or statType == 'whip':
		return float(statValue)
	else:
		return int(statValue)

# Parameters require a string for season and string with the chosen leagues initials.  
# Returns a list of dicts containing the name and stats of each player.

# new parameters... startYear, endYear and leagueInitials.  Create an index reflects the number players that have been processed for that league, 
# regardless of season.  For instance, if measuring two seasons with 11 players each, the index should go from 0 to 21.  The index will be a list of ints
# and used as a parameter for creating two objects, a series containing the cyw values (cywSeries) of each player and a dataframe containing all the other
# player info (playerDF).  These objects will be returned at the end of the function.
def getSeasonStatsCY(startYear, endYear, leagueInitials):

		# leagueStats = pd.DataFrame([])
		playerList = []
		cywList = []
		indexList = []
		currentIndex = 0
		currentYear = startYear  # currentYear will be incremented instead of startYear	

		while currentYear <= endYear:	

			r = requests.get("https://www.baseball-reference.com/awards/awards_" + str(currentYear) + ".shtml")
			
			soup = BeautifulSoup(r.text, "html.parser")

			#rawDiv = soup.find("div", {"id": "all_NL_CYA_voting"})
			cyaDivString = str(soup.find("div", {"id": "all_" + leagueInitials + "_CYA_voting"}))

			# The purpose of the following three lines of code are to remove the comment tags surrounding the CYA voting table data
			commentBeginTag = '<!--'
			commentEndTag = '-->'
			cyaDivString = cyaDivString[cyaDivString.find(commentBeginTag) + len(commentBeginTag):cyaDivString.rfind(commentEndTag)]
			
			soup = BeautifulSoup(cyaDivString, "html.parser")
			cyaTableCells = soup.findAll("td")
			
			currentStatCount = 0
			playerCount = 0
			# seasonPlayers = []
			player = {}
			# cywSeasonList = []
			# seasonStats = pd.DataFrame([])

			for tableCell in cyaTableCells:
				
				rawString = str(tableCell)
				trimmedString = rawString[rawString.find('>') + 1:rawString.rfind('<')]
				
				if currentStatCount == 0:
					trimmedString = trimmedString[trimmedString.find('>') + 1:trimmedString.rfind('<')]
					player = {'season':currentYear, 'league': leagueInitials, 'name': trimmedString}

					# The first player of each season is always the CY winner for that season and league.  Winners have a cyw value of 1.
					if playerCount == 0:
						cyw = 1
					else:
						cyw = 0
				else:
					stat = tableCell['data-stat']

					statValue = evaluateStatType(stat, trimmedString)

					player[stat] = statValue

				
				currentStatCount = currentStatCount + 1
				
				if currentStatCount%30 == 0:
					currentStatCount = 0
					playerCount = playerCount + 1
					playerList.append(player)
					cywList.append(cyw)
					indexList.append(currentIndex)
					currentIndex = currentIndex + 1
					print(playerCount)

			#leagueStats = leagueStats.concat(leagueStats, pd.DataFrame())	
			currentYear = currentYear + 1	

		leagueStats = pd.DataFrame(playerList, indexList)
		cywRecord = pd.Series(cywList, indexList)
		return leagueStats, cywRecord


# Take a dataframes and display their information in a graph.
def graphStatData(stats):
	
	#graph = sns.displot(data=stats, x='team_ID', col='league')
	#graph.set_xticklabels(rotation=90)
	avgInnings = stats['IP'] / stats['G']
	sns.relplot(
		data=stats,
		x=avgInnings, y='earned_run_avg', 
		hue='cyw'
	)	
	plt.show()

# Create a list of features from the labels of the columns in the dataframe.  Remove cya and any non-numeric features.  
# Make the target cya.  Assign the values of the features to 'X' and the values of the targets to 'y'.  
# Split the data into training and test sets, intialize and fit object, and standardize features of 'X' train and test.
# Data is a dataframe, target is a series.
def trainLogisticRegressionModel(stats):

	features = stats.columns.to_list()
	features.remove('cyw')
	features.remove('team_ID')
	features.remove('league')
	features.remove('name')

	X = stats[features]
	print(X.info())
	y = stats['cyw']
	print(y)

# Create a list of player dicts that contains the players of both leagues.  Each league will also have a separate list.
def ScraperMain():



	# Update the following input command to instead be a new function that can parse the input for multiple years 
	# or year ranges, separated by commas and hyphens respectively.
	input("Hit enter to collect CYA voting data")
	#print(seasonString)
	#if not(seasonString == "quit") and checkSeason(int(seasonString)):
	

	# Start with 1967 and gather data for each season up to and including 2020.
	currentYear = 2020
	endYear = 2020	
	#dfMLB = pd.DataFrame([])
	# Create empty dataframes for each leagues stats
	statsAL, cywAL = getSeasonStatsCY(2019, 2020, 'AL')
	#statsNL = pd.DataFrame([])

		
	#	statsAL = pd.concat([statsAL, pd.DataFrame(getSeasonStatsCY(currentYear, "AL"))])

	#	dfNL = pd.DataFrame(getSeasonStatsCY(currentYear, "NL"))

		#dfMLB = pd.concat([dfMLB, dfAL, dfNL])
	#	currentYear = currentYear + 1
	#graphStatData(dfMLB)	
	
			
	#trainLogisticRegressionModel(statsAL)

	print(statsAL.loc[[0]])
	print(cywAL[0])

	print(statsAL.loc[8])
	print(cywAL[8])


ScraperMain()