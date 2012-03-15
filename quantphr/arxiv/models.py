from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

#>>> from arxiv.models import Author, Paper
#>>> Author.objects.all()
#[]
## Create a new Poll.
#>>> import datetime
#>>> p = Poll(question="What's up?", pub_date=datetime.datetime.now())
#>>> p.save()

## Here is some simple sample code for managing the database manually in ./manage.py shell: 
## Good info on database queries is at https://docs.djangoproject.com/en/dev/topics/db/queries/
# e.g., Entry.objects.filter(blog__name__exact='Beatles Blog') finds all blog entries whose blog has a particular name
## Manually delete the version information from the end of the arXiv hyperlinks: 
## 	e.g., http://arxiv.org/abs/1111.1971v1 -> http://arxiv.org/abs/1111.1971
#from arxiv.models import *
#import re
#papers = Paper.objects.all()
#for paper in papers: 
#	paper.linkAbsPage = re.sub(r"v\d+$", "", paper.linkAbsPage)		# or use re.split('v\d+$', paper.linkAbsPage)[0]
#	paper.linkPdf = re.sub(r"v\d+$", "", paper.linkPdf)
#	paper.save()
## Clear the favorites information (counts and user fields) from all papers: 
#papers = Paper.objects.all()
#for paper in papers: 
#	paper.numFavorites = 0
#	paper.save()

## To add new fields to *existing* models, use South --- Django will not itself touch existing models.  In that case, don't forget to edit admin.py to add the fields to the admin form.  ./manage.py schemamigration arxiv --auto; ./manage.py migrate arxiv

# To change field names, use 
#>>> python manage.db sqlall arxiv
# Find the new line, run python manage.db dbshell and type in something like: 
# ALTER TABLE books_book ADD COLUMN num_pages integer;		<-- or whatever the new line is
# ALTER TABLE arxiv_paper ADD COLUMN linkPdf varchar;
# ALTER TABLE books_book DROP COLUMN num_pages;		<-- remove standard column
# DROP TABLE books_books_publishers;				<-- remove many-to-many field
# DROP TABLE books_book; 							<-- remove models

class Author(models.Model):
	name = models.CharField(max_length=100)		# this is the unicode-encoded full name of the author
		# we do not support one author having >1 name.  there is also no support for merging authors, for now
		# should add an arXiv search url, e.g., 'http://arxiv.org/find/all/1/au:+Lezama_A/0/1/0/all/0/1'
	def __unicode__(self):
		return self.name
	

class Paper(models.Model): 
		# Django's built-in fields are listed at https://docs.djangoproject.com/en/dev/ref/models/fields/
		
		# basic paper information from the arXiv --- note that we are *not* currently setting the primary key in the database to be the arxivId, it is just id
	arxivId = models.CharField('arXiv ID', max_length=9)
	title = models.CharField(max_length=300)
	abstract = models.TextField(None)	# could also use a CharField, with a generous max_length --- Postgresql treats a CharField as 'varchar(300)', e.g., and a TextField as 'text'
	date_published = models.DateTimeField()		# this is the date and time the article was posted (can be different from the arXiv mailing date)
	date_mailed = models.DateField()		# this is the *approximate* date the arXiv mailing went out (based on EST)
	authors = models.ManyToManyField(Author)
	category = models.CharField(max_length=20)
	categories = models.CharField(max_length=100)	# we do not currently validate the length
	version = models.IntegerField(blank=True, null=True)
	linkAbsPage = models.URLField('abstract link')	# first argument is a human-readable field name (not capitalized)
	linkPdf = models.URLField('pdf link')

		# additional fields for the quantphr application
	favorites = models.ManyToManyField(User, blank=True)	# one cool possibility (not done here) is to have a ManyToMany relationship through an intermediary object that can have extra data on the relationship, e.g., in this case the time the favorite relationship was created --- see https://docs.djangoproject.com/en/dev/topics/db/models/#intermediary-manytomany
	numFavorites = models.IntegerField(default=0, help_text="counts favorites from registered and anonymous users")
		# anonymous users' favorites are not otherwise stored in the database, but are tracked by cookies in the session
	#comments = ...
	#keywords = ...
	
	def __unicode__(self): 
		return self.arxivId + " " + self.title
	class Meta: 
		ordering = ['-numFavorites', '-date_mailed', 'arxivId']	# by default sort backward by date, then forward by ID
	