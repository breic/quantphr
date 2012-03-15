#!/usr/bin/env python
# On Heroku, schedule a job "python quantphr/dailyupdate.py" or run it from the shell with "heroku run python quantphr/dailyupdate.py"

print "Running daily update..."

from django.core.management import setup_environ
import settings

setup_environ(settings)

import arxiv
from arxiv.daily import getLatestArxivPapers, getLastWeeksPapers, dbSavePapersAndAuthors

	# this is some dummy code for testing
numNewRSSPapers, numNewRSSAuthors = 1, 2
numNewWeeklyPapers, numNewWeeklyAuthors = 10, 11

	# download the RSS feed, parse it, sleep, download the paper information, add them to the db
numNewRSSPapers, numNewRSSAuthors = getLatestArxivPapers()
numNewWeeklyPapers, numNewWeeklyAuthors = getLastWeeksPapers()	# next download all papers for the last week
