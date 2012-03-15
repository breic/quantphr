from django.template.loader import get_template
from django.template import RequestContext, Context
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

import datetime, random, operator

from arxiv import models

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def exportFavorites(request):
	"""Returns all the user's favorites as a simple text file."""
	favorites = models.Paper.objects.filter(
		favorites__id = request.user.id
	).order_by( 'arxivId' )
	ids = [(paper.arxivId + ' ' + paper.title) for paper in favorites]
	response = '%s Favorites for %s:\n' % (datetime.date.today(), request.user.username)
	response = response + '\n'.join(ids)
	return render_to_response('exportFavorites.txt', {'favorites': response}, context_instance=RequestContext(request), mimetype='text/css')

@login_required
def displayFavorites(request):
	"""This isn't really set up yet.  Should implement pagination."""
	favorites = models.Paper.objects.filter(
		favorites__id = request.user.id
	)
	
	papersList = PapersList(favorites, datetime.date.today())
	preparePapersListForRendering(request, papersList)
	allPapersLists = [papersList]
	
	return render_to_response('latest_papers.html', 
		{'allPapersLists': allPapersLists, 
		 'days': 1, 
		 'bunched': True, 
		 'uniqueKey': random.random(),	# used to check if page is loaded from the cache --- might be better to wrap render_to_response
		 'isChrome': ('Chrome' in request.META['HTTP_USER_AGENT'])
		}, 
		context_instance=RequestContext(request))

@login_required
#@permission_required('polls.can_vote', login_url="/login/")
def updatePapers(request):
	"""
	View for an admin URL that manually runs the script to check the latest arXiv papers.
	
	It might be nice to have a meaningful template that shows status information using Ajax.  
	(OnLoad it could send an Ajax request that starts the script, with a callback function 
	that updates a status feed.  For partial statuses, the first callback function could start 
	another Ajax query, or maybe there is a better way.)
	Also there should be graceful behavior and alerts for errors that occur.  
	"""
	if not request.user.is_staff:	# or is_superuser
		raise Http404()
	from arxiv.daily import getLatestArxivPapers, getLastWeeksPapers, dbSavePapersAndAuthors
		# this is some dummy code for testing
	numNewRSSPapers, numNewRSSAuthors = 1, 2
	numNewWeeklyPapers, numNewWeeklyAuthors = 10, 11
		# download the RSS feed, parse it, sleep, download the paper information, add them to the db
	numNewRSSPapers, numNewRSSAuthors = getLatestArxivPapers()
	numNewWeeklyPapers, numNewWeeklyAuthors = getLastWeeksPapers()	# next download all papers for the last week
	return render_to_response('update_papers.html', locals())	# locals() passes a dictionary of all local variables

class PapersList:
	@staticmethod
	def formatDateRange(firstDate, lastDate):
		"""Takes two datetime.date objects, and formats the range, e.g., 'Nov 10-11, 2011'.
		
		It turns out that there is a built-in Django template filter for date formatting, which 
		might be cleaner to use.  (E.g., unlike the Python date.strftime() function, it can format
		a one-digit day without a leading 0.)
		See https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date .  
		"""
		if (not lastDate) or firstDate == lastDate: 
			return firstDate.strftime("%a, %b") + " %d" % (firstDate.day,)
		if firstDate.month == lastDate.month: 
			return firstDate.strftime("%B") + " %d-%d" % (firstDate.day,lastDate.day)
		return firstDate.strftime("%B") + " %d - " % (firstDate.day,) + lastDate.strftime("%B") + " %d" % (lastDate.day,)
	
	def __init__(self, papers, firstDate, lastDate=None):
		self.papers = papers
		if firstDate: 
			self.date = PapersList.formatDateRange(firstDate, lastDate)

def getPapersForDates(firstDate, lastDate=None, maxPapers=100):
	if not lastDate: lastDate = firstDate
	papers = models.Paper.objects.filter(
		category__exact = 'quant-ph'
	).filter(	# date_mailed__gte=, date_mailed= , ...
		date_mailed__gte = firstDate
	).filter(
		date_mailed__lte = lastDate
	).order_by(
		'-numFavorites', '-date_mailed', 'arxivId'	# this is the default ordering, but it doesn't hurt to be explicit
	)[:maxPapers]
	return papers

def getUnbunchedPapersLists(endDate, days):
	allPapersLists = []
	for day in range(days): 
		date = endDate + datetime.timedelta(days=-day)
		papers = getPapersForDates(date)
		if len(papers) == 0: continue
		papersList = PapersList(papers, date)
		allPapersLists.append(papersList)
	return allPapersLists

def getBunchedPapersLists(endDate, days):
	startDate = endDate + datetime.timedelta(days=-days+1)
	papers = getPapersForDates(startDate, endDate)
	papersList = PapersList(papers, startDate, endDate)
	return [papersList]

def preparePapersListForRendering(request, papersList):
	papers = papersList.papers
	for paper in papers: 
		paper.authorsList = paper.authors.all() # take the authors list from the database---possibly this could be stored there
		paper.isFavorite = (request.user in paper.favorites.all())
	if not request.user.is_authenticated(): 
		# save in the session the list of visible papers (just the IDs)
		# so that when the user logs in we can return a list of that user's favorites on the current page
		arxivIds = [paper.arxivId for paper in papers]
		visiblePapers = request.session.get('visible_papers', []) + arxivIds
		#print "saved to session the visible %d papers" % (len(arxivIds),), arxivIds
		request.session['visible_papers'] = visiblePapers

def addPapersForDate(request, day):
	"""Returns the HTML for a single day, a certain number of days back from the last arXiv mailing.
	
	This is called by the Ajax function to load more days of papers.
	"""
	try: 
		day = int(day)
	except ValueError: 
		raise Http404()
	latestDateMailed = request.session.get('latestDateMailed', models.Paper.objects.filter(category__exact='quant-ph').order_by('-date_mailed')[0].date_mailed)
		
	finalDay = day		# find the previous arXiv mailing (could be a few days back, e.g., over a weekend)
	while finalDay < min(day+5, 100): 
		date = latestDateMailed + datetime.timedelta(days=-finalDay+1)
		papers = getPapersForDates(date)
		if len(papers) > 0: break
		finalDay += 1
	if len(papers) == 0: return		# should only happen if we reach the end of the database...
	
	papersList = PapersList(papers, date)
	preparePapersListForRendering(request, papersList)
		
	t = get_template('papersList.html')
	c = RequestContext(request, {'papersList': papersList, 'bunched': True})
	s = t.render(c)
	return t.render(c), finalDay

def renderPapersLists(request, allPapersLists, days, bunched):
	for papersList in allPapersLists: 
		preparePapersListForRendering(request, papersList)
		
	#t = get_template('current_datetime.html')
	#html = t.render(Context({'current_date': now}))
	#return HttpResponse(html)
	
	# when there are multiple days, should they be mashed together, sorted by stars, or kept separate?
	# if the latter, then should return a list of lists, each one starting with the date
	# I like the date format, "10 Nov '11"
	return render_to_response('latest_papers.html', 
		{'allPapersLists': allPapersLists, 
		 'days': days, 
		 'bunched': bunched, 
		 'uniqueKey': random.random(),	# used to check if page is loaded from the cache --- might be better to wrap render_to_response
		 'isChrome': ('Chrome' in request.META['HTTP_USER_AGENT'])
		}, 
		context_instance=RequestContext(request))

def displayPapers(request, days='2', bunched=False): # days='1' means that one day's mailing is returned
	try: 	# although url.py should validate days to match \d{1,2}, we validate it again
		daysInt = int(days)
	except ValueError: 
		raise Http404()
	latestDateMailed = models.Paper.objects.filter(category__exact='quant-ph').order_by('-date_mailed')[0].date_mailed	# .order_by('-date_mailed')[0] can also be written .latest('date_mailed')
	request.session['latestDateMailed'] = latestDateMailed		# store in the session --- so that later Ajax requests don't have to recompute the date (which could change passing midnight)	
	if bunched: 
		allPapersLists = getBunchedPapersLists(latestDateMailed, daysInt)
	else: 
		allPapersLists = getUnbunchedPapersLists(latestDateMailed, daysInt)
	return renderPapersLists(request, allPapersLists, daysInt, bunched)

def logout_view(request):
	logout(request)
	return redirect('/')
	

# Both quantphr.css and quantphr.js should be made static (especially the latter, which is!)
#def css(request):	# now made static
#	return render_to_response('quantphr.css', context_instance=RequestContext(request), mimetype='text/css')
#def js(request): # now made static
#	return render_to_response('quantphr.js', context_instance=RequestContext(request), mimetype='text/javascript')