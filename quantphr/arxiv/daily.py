import re
#from datetime import datetime, date, timedelta
import datetime
import pytz		# package for converting between time zones, including daylight-savings time; see http://pytz.sourceforge.net/

import feedparser	# from http://code.google.com/p/feedparser/

from models import Author, Paper

def mailingDate(date):
	"""Returns an *approximate* date for the arXiv mailing announcing a paper with the input posting date.
	
	This is not accurate.  It is almost impossible to get completely accurate mailing dates, because the 
	arXiv takes holidays and sometimes misses mailings for unscheduled technical problems.  
	To get accurate information, the announcement date should be set when the paper is announced, from the 
	arXiv's RSS feed.  This only works for newly announced papers, though.  
	The most reasonable approximation to mailing dates for previously announced papers, though, is to convert 
	the paper's time zone to EST and then check the day of the week and compare to 4pm.  Since this function 
	is only going to be used to back-populate the database and the exact mailing date is not important for 
	old papers, we only compare to 4pm and don't both adjusting for weekends.  
	"""
	
	def dateUTCtoEST(date):
		"""Converts UTC time to EST, taking daylight savings into account.

		The input datetime object is assumed to be naive (i.e., without any timezone information included).  
		We use the pytz package to add the UTC time zone, then to convert to EST.  
		"""
		return pytz.utc.localize(date).astimezone(pytz.timezone('US/Eastern'))
	
	date_est = dateUTCtoEST(date)
	date_cutoff = date_est.replace(hour=16)
	if date_est <= date_cutoff: # made the 4pm deadline --- add one day to get the official mailing date
		offset_days = 1
	else: 
		offset_days = 2
	return date_est.date() + datetime.timedelta(days=offset_days)

def dbSavePapersAndAuthors(papers, latestMailing=True):
	"""Saves an array of paper information into the database.  Returns numbers of new papers and authors added.  
	
	If the latestMailing argument is true, then sets the paper dates to either today or tomorrow, 
	regardless of the date from the arXiv.  It sets to today if the function is run before 8pm ET, and to 
	tomorrow otherwise.  The idea is that this function should be run regularly every day, the night that the 
	mailing goes out.  If run late in the day before midnight, then the mailing has tomorrow's date.  If run 
	early in the day, e.g., if for some reason it didn't run when it should have, then the mailing was sent out 
	yesterday and is for today.  
	"""
	if latestMailing: 
		latestMailingDate = datetime.date.today()
		now = datetime.datetime.now(pytz.timezone('US/Eastern'))
		cutoff = now.replace(hour=20,minute=0,second=0,microsecond=0)
		if now > cutoff: 
			latestMailingDate += datetime.timedelta(days=+1)	# note: The official mailing date is the day the email goes out, a few hours after the paper was made available
	numNewPapersAdded = numNewAuthorsAdded = 0
	for paper in papers: 
		authors = []
		for author in paper['authors']: 
			authorsWithSameName = Author.objects.filter(name=author)
			if authorsWithSameName: 		# author with same name already exists in database---don't add a duplicate
				a = authorsWithSameName[0]	# there might be duplicates --- take the first (maybe fix later)
			else: 
				a = Author(name=author)
				a.save()
				numNewAuthorsAdded += 1
			authors.append(a)
		if Paper.objects.filter(arxivId=paper['arxivId']): continue		# NOTE: If we make a mistake adding the paper the first time, this line will keep the code below from ever running to fix it
		if latestMailing: 
			mailing_date = latestMailingDate
		else: 
			mailing_date = mailingDate(paper['datePublished'])
		p = Paper(
			arxivId = paper['arxivId'],
			title = paper['title'],
			abstract = paper['abstract'],
			date_published = paper['datePublished'],
			date_mailed = mailing_date,
			#authors = authors, 	# ManyToManyField is set up later
			category = paper['category'],
			categories = paper['categories'],
			version = paper['version'],
			linkAbsPage = paper['linkAbsPage'],
			linkPdf = paper['linkPdf']
		)
		p.save()	# need to save before setting up the ManyToMany field of authors
		for author in authors: 	# alternatively, to clear a ManyToMany field, use p.authors.clear()
			p.authors.add(author)
		p.save()
		numNewPapersAdded += 1
	print "%d new papers, %d new authors added" % (numNewPapersAdded, numNewAuthorsAdded)
	return numNewPapersAdded, numNewAuthorsAdded

def processPaperIds(identifiers, sleepFirst=True, versionMask=(lambda v: v==1), categoryMask=('quant-ph',), lookupOldPapers=False):
	"""Takes a list of paper identifiers and downloads and processes their info from the arXiv.
	
	The lookupOldPapers argument says whether to look up papers that are already present in the database.  
	(Note, though, that we aren't storing non quant-ph papers, so many old papers will not be filtered out.)
	"""
	
	if sleepFirst: 		# since this is generally called after a previous arXiv request, it is polite to pause briefly before sending the next request
		wait_time = 3
		print "Sleeping for %i seconds..." % wait_time
		from time import sleep
		sleep(wait_time)
	
	if not lookupOldPapers: 
		identifiers = filter(lambda p: not Paper.objects.filter(arxivId=p).exists(), identifiers)
	
	queryUrl = 'http://export.arxiv.org/api/query?max_results=100&id_list=' + ','.join(identifiers)
	print "Downloading paper information... %s" % queryUrl
	feed = feedparser.parse(queryUrl)

	print "Processing papers..."	
	papers = []
	for entry in feed.entries:
		paper = {}		# just use a dictionary until we have better paper information
		paper['arxivId'] = entry.id.split('/abs/')[-1]
		paper['title'] = ' '.join(entry.title.split())	# splits out whitespace and new lines; could also use .replace('\n', '').replace('  ', ' ')
		paper['abstract'] = ' '.join(entry.summary.split())		# eliminate all \n new lines
			# this is the date and time the paper was posted --- which might or might not be before the date the arXiv mailing went out
		paper['datePublished'] = datetime.datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
		try: 
			paper['authors'] = [x['name'] for x in entry.authors]	# entry.authors starts as a list of {'name':'John'} items
		except AttributeError: 
			paper['authors'] = [{'name':entry.author}]
		# get the links to the abs page and pdf for this e-print --- strip off version info
		for link in entry.links:
			if link.rel == 'alternate':
				paper['linkAbsPage'] = re.split('v\d+$', link.href)[0]
			elif link.title == 'pdf':
				paper['linkPdf'] = re.split('v\d+$', link.href)[0]
		# to get the primary category, just take the first element in entry.tags --- a hack
		paper['category'] = entry.tags[0]['term']
		paper['categories'] = ', '.join([t['term'] for t in entry.tags])
		papers.append(paper)
	
	newPapers = []
	for paper in papers: 
		arxivId, version = re.split('v', paper['arxivId'])
		paper['arxivId'] = arxivId
		paper['version'] = version = int(version)
		if versionMask and not versionMask(version): continue
		if categoryMask and not paper['category'] in categoryMask: continue
		newPapers.append(paper)
	
	return newPapers

def getLatestPaperIds(categoryMask=('quant-ph',)): 
	"""Returns a list of the IDs xxxx.xxxx that have been updated in the last day.
	
	Taken from the arXiv RSS feed, at, e.g., http://export.arxiv.org/rss/quant-ph.
	The arXiv doesn't allow searching by date.  
	Updated papers includes new, cross-listed and replaced papers.  
	"""
	### NOTE: Only one arXiv category can be loaded at a time.
	rssUrl = "http://export.arxiv.org/rss/" + categoryMask[0]
	print "Downloading arXiv rss feed... %s" % rssUrl
	updatedpaperitems = feedparser.parse(rssUrl)['items']
	identifiers = []
	for item in updatedpaperitems: 
		match = re.search("\d{4}\.\d{4}$", item['id'])
		if not match: continue
		identifier = match.group(0)
		identifiers.append(identifier)
	return identifiers

def getLatestArxivPapers(versionMask=(lambda v: v==1), categoryMask=('quant-ph',)):
	"""
	Gets information for the latest posted arXiv papers.
	
	(See http://arxiv.org/help/api/user-manual for details.)
	
	NOTE: There is no error handling.  
	If the arXiv web site is slow for some reason, the code might fail in a bad way?  
	If the arXiv changes its formats, e.g., for dates, this will not work at all.  
	NOTE: Only one arXiv category can be loaded at a time.  
	
	Here is an example of the second query: http://export.arxiv.org/api/query?max_results=100&id_list=1111.1734,1111.1746,1111.1774,1111.1781,1111.1805,1111.1853,1111.1864,1111.1869,1111.1877,1111.1885,1111.1907,1111.1934,1111.1960,1111.1962,1111.1971,1111.1978,1111.1979,1111.1986,1111.1997,1111.2004,1111.2012,1111.2026,1111.2041,0912.1607,1004.3880,1006.4027,1105.4531,1106.2178,1109.0147,1109.2560,1109.5756,1110.4690,1110.6566,1110.6725,1111.0675,1111.0837,1111.1646,1106.4968,1111.0781
	
	There is some possibly useful code at dailyarxiv.com/arxiv-list.html?search_query=cat:quant-ph*&day=8&month=10&year=2010
	"""
	identifiers = getLatestPaperIds(categoryMask=categoryMask)

	papers = processPaperIds(identifiers, versionMask=versionMask, categoryMask=categoryMask, lookupOldPapers=True)
	numNewPapersAdded, numNewAuthorsAdded = dbSavePapersAndAuthors(papers, latestMailing=True)
	return numNewPapersAdded, numNewAuthorsAdded

def getLastWeeksPapers(versionMask=(lambda v: v==1), categoryMask=('quant-ph',)):
	"""Populates the database with up to 500 quant-ph papers (other categories not supported) from the last week.
	"""
	from urllib import urlopen
	fp = urlopen('http://arxiv.org/list/quant-ph/pastweek?show=500')
	try: 
		data = fp.read()
	finally: 
		fp.close()
	identifiers = map(unicode, re.findall(r'arXiv:(\d{4}\.\d{4})', data))
	papers = processPaperIds(identifiers, versionMask=versionMask, categoryMask=categoryMask, lookupOldPapers=False)
	numNewPapersAdded, numNewAuthorsAdded = dbSavePapersAndAuthors(papers, latestMailing=False)
	return numNewPapersAdded, numNewAuthorsAdded

## Here is some testing code: 
# from arxiv.daily import getLatestArxivPapers, dbSavePapersAndAuthors
#p = newPapers = getLatestArxivPapers()
def testArxivDownload():
	"""Code to test the getLatestArxivPapers() function."""
	p = newPapersQuantph = getLatestArxivPapers()
	for paper in newPapersQuantph: 
		print paper['arxivId'], paper['title']
		print paper['datePublished']

# to run the doctests, run python or python -v directly on this script
if __name__ == "__main__":
	import doctest
	doctest.testmod()