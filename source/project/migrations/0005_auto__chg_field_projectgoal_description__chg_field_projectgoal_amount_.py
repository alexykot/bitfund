# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ProjectGoal.description'
        db.alter_column('project_projectgoal', 'description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'ProjectGoal.amount'
        db.alter_column('project_projectgoal', 'amount', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=0))

        # Changing field 'ProjectNeed.description'
        db.alter_column('project_projectneed', 'description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'ProjectNeed.amount'
        db.alter_column('project_projectneed', 'amount', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=0))

    def backwards(self, orm):

        # Changing field 'ProjectGoal.description'
        db.alter_column('project_projectgoal', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'ProjectGoal.amount'
        db.alter_column('project_projectgoal', 'amount', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=0))

        # Changing field 'ProjectNeed.description'
        db.alter_column('project_projectneed', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'ProjectNeed.amount'
        db.alter_column('project_projectneed', 'amount', self.gf('django.db.models.fields.DecimalField')(max_digits=6, decimal_places=0))

    models = {
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
        },
        'project.project': {
            'Meta': {'object_name': 'Project'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 17, 15, 22, 2, 2)'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'maintainer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'regular_need': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '0', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectfeaturerequest': {
            'Meta': {'object_name': 'ProjectFeatureRequest'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'project.projectgoal': {
            'Meta': {'object_name': 'ProjectGoal'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '0'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 17, 15, 22, 2, 2)'}),
            'date_ending': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectneed': {
            'Meta': {'object_name': 'ProjectNeed'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '0'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 17, 15, 22, 2, 2)'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['project']