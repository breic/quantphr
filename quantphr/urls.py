from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout

#from settings import SITE_MEDIA_PATH

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#from quantphr import settings
from django.conf import settings
from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

urlpatterns = patterns('',
	(r'^$', 'views.displayPapers', {'bunched': False}),
	(r'^papers/favorites/export/$', 'views.exportFavorites'),
	(r'^papers/favorites/$', 'views.displayFavorites'),
	(r'^papers/latest/$', 'views.displayPapers', {'bunched': False}),
	(r'^papers/latest/(\d{1,2})/$', 'views.displayPapers', {'bunched': False}),
	(r'^papers/sorted/$', 'views.displayPapers', {'bunched': True}),
	(r'^papers/sorted/(\d{1,2})/$', 'views.displayPapers', {'bunched': True}),
	#(r'^css/quantphr.css$', 'views.css'),	# moved to static
	#(r'^js/quantphr.js$', 'views.js'),	# moved to static
	(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
	(r'^accounts/login/$', login),
    (r'^accounts/logout/$', 'views.logout_view'),
	
	#url(r'', include('social_auth.urls')),	# for django-social-auth
	(r'^openid/', include('django_openid_auth.urls')), # for django-openid-auth
	#(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : SITE_MEDIA_PATH}),
	
	# Examples:
	# url(r'^$', 'quant-phr.views.home', name='home'),
	# url(r'^quant-phr/', include('quantphr.foo.urls')),
	
	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	
	# Uncomment the next line to enable the admin:
	url(r'^admin/update-papers/$', 'views.updatePapers'),
	url(r'^admin/', include(admin.site.urls)),
)
