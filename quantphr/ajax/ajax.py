from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from dajaxice.decorators import dajaxice_register
from django.contrib import auth

import re

from arxiv import models

class BadIdError(Exception):
	def __init__(self):
		pass
	def __str__(self):
		return super.self

@dajaxice_register 
def getMorePapers(request, days):
	#print "in getMorePapers" 
	#print "[%d]" % (days,)
	from quantphr import views
	newHTML, finalDays = views.addPapersForDate(request, days)
	#print newHTML
	newHTML = '<span><div class="interday-spacer"></div>' + newHTML + '</span>'		# we only add the first container to the HTML, so must wrap everything in a span
	print "finalDays", finalDays
	#print newHTML
	return simplejson.dumps({'newHTML': newHTML, 'finalDays': finalDays})

@dajaxice_register
def getFavorites(request): 
	user = request.user
	if not user.is_authenticated(): return
		# if the currently visible papers are saved in the session, then we only return the user's 
		#  currently visible favorites
		# otherwise, we return all of his favorites (but this should not happen)
	visibleArxivIds = request.session.get('visible_papers')
	if visibleArxivIds: 
		objects = models.Paper.objects.filter(arxivId__in=visibleArxivIds)
	else: 
		objects = models.Paper.objects
	userFavorites = objects.filter(favorites__id=user.id)
	arxivIds = [paper.arxivId for paper in userFavorites]
	#print arxivIds
	return simplejson.dumps({'arxivIds': arxivIds})

@dajaxice_register
def login(request, username, password):
	#print username, password
	user = auth.authenticate(username=username, password=password)
	if user is not None and user.is_active:
		# Correct password, and the user is marked "active"
		print "Logging in user", username
		auth.login(request, user)
		# Redirect to a success page.
		return simplejson.dumps({'message':'login 1', 'login':1, 'username':username})
	else:
		# Show an error page
		print "Login failed"
		return simplejson.dumps({'message':'login 0', 'login':0})

from django.core.exceptions import ValidationError
@dajaxice_register
def editProfile(request, first_name, last_name, institution):
	print "editProfile request: first_name:", first_name, "last_name:", last_name, "institution:", institution
	user = request.user
	if user.is_authenticated(): 
		user.first_name = first_name
		user.last_name = last_name
		profile = user.get_profile()
		profile.institution = institution
		try: 
			user.full_clean()
			profile.full_clean()
			user.save()
			profile.save()
		except ValidationError, e:
			print "Changes not saved: Validation error", e

def validateArxivId(arxivId):
	if not re.match(r"^\d{4}\.\d{4}$", arxivId): 
		print 'ajax argument:', arxivId
		raise BadIdError, 'input arxivId: ' + arxivId	# right now, dajaxice logger doesn't have any handlers, so it is better to print the error message manually	

@dajaxice_register
def favorite(request, arxivId):
	"""
	Fetches the paper and tries to favorite it.
	
	Should probably set a cookie for anonymous users, but currently just increments the fave count.
	"""
	print "favorite: [%s]" % (arxivId,)
	validateArxivId(arxivId)
	try: 
		paper = models.Paper.objects.get(arxivId=arxivId)
	except models.Paper.DoesNotExist: 
		print 'paper does not exist'
		raise BadIdError, 'ajax argument: ' + arxivId
	# sanitize the favorites count, just in case...
	paper.numFavorites = max(paper.numFavorites, paper.favorites.count())
	
	user = request.user
	if not user.is_authenticated(): 
		paper.numFavorites += 1
		paper.save()
		print "added anonymous fave"
	if user.is_authenticated(): 
		if not user in paper.favorites.all(): # check user hasn't already faved the paper
			paper.favorites.add(user)
			paper.numFavorites += 1
			paper.save()
			print "added authenticated fave for user %s" % (user,)
	print "now %s has %d total faves, %d of which are authenticated" % (arxivId, paper.numFavorites, paper.favorites.count())
	return simplejson.dumps({'message': paper.title, 'arxivId': arxivId, 'numFavorites': paper.numFavorites})

@dajaxice_register
def unfavorite(request, arxivId):		# right now, does nothing
	print "unfavorite: [%s]" % (arxivId,)
	validateArxivId(arxivId)
	try: 
		paper = models.Paper.objects.get(arxivId=arxivId)
	except models.Paper.DoesNotExist: 
		print 'paper does not exist'
		raise BadIdError, 'ajax argument: ' + arxivId
	
	user = request.user
	if not user.is_authenticated() and paper.numFavorites > paper.favorites.count(): 
		# numFavorites counts the total number of favorites, from logged-in and anonymous users.  If the unfavorite request is from an anonymous user, then decrement the total favorites count.  (Yes, one anonymous user could still unfavorite the same paper over and over...)
		paper.numFavorites -= 1
		paper.save()
		print "removed anonymous fave"
	if user.is_authenticated(): 
		if user in paper.favorites.all(): 	# check that the user has favorited the paper (we could also do this with a SQL query instead of querying the database for all users and then checking in python)
			paper.favorites.remove(user)
			paper.numFavorites -= 1
			paper.save()
			print "removed authenticated fave for user %s" % (user,)
	print "now %s has %d total faves, %d of which are authenticated" % (arxivId, paper.numFavorites, paper.favorites.count())
	# this shouldn't be necessary, but in case of weird situations let's sanitize the favorites count
	paper.numFavorites = max(paper.numFavorites, paper.favorites.count())
	return simplejson.dumps({'arxivId': arxivId, 'numFavorites': paper.numFavorites})

#@dajaxice_register	# decorator equivalent to calling dajaxice_functions.register(myexample) after the function def
def myexample(request):
	print 'myexample'
	return simplejson.dumps({'message':'Hello World'})
dajaxice_functions.register(myexample)

def example1(request):
	""" First simple example """
	print 'example1'
	return simplejson.dumps({'message': 'hello world'})
dajaxice_functions.register(example1)

def example2(request):
	""" Second simple example """
	print 'example2'
	return simplejson.dumps({'numbers': [1, 2, 3]})
dajaxice_functions.register(example2)

def example3(request, data, name):
	result = sum(map(int, data))
	return simplejson.dumps({'result': result})
dajaxice_functions.register(example3)

def error_example(request):
	raise Exception("Some Exception")
dajaxice_functions.register(error_example)
