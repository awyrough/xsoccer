# functions centered around statistics

"""

"""
import time
import datetime 
import numpy as np 
from scipy import stats
from scipy.stats import ttest_ind, ttest_1samp
from scipy.stats.distributions import norm


from eventstatistics.models import EventStatistic
from games.models import Game
from lineups.models import Lineup
from players.models import Player
from playerstatistics.models import PlayerStatistic
from salaries.models import Salary
from statistictypes.models import StatisticType
from teams.models import Team
from teamstatistics.models import TeamStatistic
from venues.models import Venue

def welchs_ttest(sample1, sample2):
	"""Compute the z-score, p-value, means tied to two different samples from two different populations"""

	ttest = stats.ttest_ind(sample2, sample1)
	
	return ttest[0], ttest[1], (np.mean(sample1), len(sample1)), (np.mean(sample2), len(sample2))
