from django.contrib import admin
from arxiv.models import Author, Paper

from django.forms import TextInput, Textarea
from django.db import models


class PaperAdmin(admin.ModelAdmin):
	list_display = ('arxivId', 'title', 'date_mailed', 'numFavorites')
	list_filter = ('date_mailed',)
	search_fields = ('arxivId', 'title',)
	date_hierarchy = 'date_mailed'
	ordering = ('-arxivId',)
	fields = ('arxivId', 'title', 'numFavorites', 'favorites', 'authors', 'date_mailed', 'date_published', 'abstract', 'linkAbsPage', 'linkPdf', 'category', 'categories', 'version')
	filter_horizontal = ('favorites', 'authors',)
	formfield_overrides = {
			models.CharField: {'widget': TextInput(attrs={'size':'80'})},
			models.TextField: {'widget': Textarea(attrs={'rows':10, 'cols':80})},
		}

class AuthorAdmin(admin.ModelAdmin):
	search_fields = ('name',)


admin.site.register(Author, AuthorAdmin)
admin.site.register(Paper, PaperAdmin)