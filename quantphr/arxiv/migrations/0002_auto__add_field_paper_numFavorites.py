# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Paper.numFavorites'
        db.add_column('arxiv_paper', 'numFavorites', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding M2M table for field favorites on 'Paper'
        db.create_table('arxiv_paper_favorites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('paper', models.ForeignKey(orm['arxiv.paper'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('arxiv_paper_favorites', ['paper_id', 'user_id'])


    def backwards(self, orm):
        
        # Deleting field 'Paper.numFavorites'
        db.delete_column('arxiv_paper', 'numFavorites')

        # Removing M2M table for field favorites on 'Paper'
        db.delete_table('arxiv_paper_favorites')


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
            'favorites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linkAbsPage': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'linkPdf': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'numFavorites': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'version': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['arxiv']
