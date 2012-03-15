# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Author'
        db.create_table('arxiv_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('arxiv', ['Author'])

        # Adding model 'Paper'
        db.create_table('arxiv_paper', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('arxivId', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
            ('date_published', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_mailed', self.gf('django.db.models.fields.DateField')()),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('categories', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('version', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('linkAbsPage', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('linkPdf', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('arxiv', ['Paper'])

        # Adding M2M table for field authors on 'Paper'
        db.create_table('arxiv_paper_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('paper', models.ForeignKey(orm['arxiv.paper'], null=False)),
            ('author', models.ForeignKey(orm['arxiv.author'], null=False))
        ))
        db.create_unique('arxiv_paper_authors', ['paper_id', 'author_id'])


    def backwards(self, orm):
        
        # Deleting model 'Author'
        db.delete_table('arxiv_author')

        # Deleting model 'Paper'
        db.delete_table('arxiv_paper')

        # Removing M2M table for field authors on 'Paper'
        db.delete_table('arxiv_paper_authors')


    models = {
        'arxiv.author': {
            'Meta': {'object_name': 'Author'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'arxiv.paper': {
            'Meta': {'ordering': "['-date_mailed', 'arxivId']", 'object_name': 'Paper'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'arxivId': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['arxiv.Author']", 'symmetrical': 'False'}),
            'categories': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'date_mailed': ('django.db.models.fields.DateField', [], {}),
            'date_published': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linkAbsPage': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'linkPdf': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'version': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['arxiv']
