# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        """
        # Adding model 'ProjectCategory'
        db.create_table('project_projectcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 14, 0, 0))),
        ))
        db.send_create_signal('project', ['ProjectCategory'])
        """
        """
        # Adding model 'Project'
        db.create_table('project_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('maintainer_id', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['auth.User'])),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('brief', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 14, 0, 0))),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='unclaimed', max_length=80)),
        ))
        db.send_create_signal('project', ['Project'])
        """

        """
        # Adding M2M table for field categories on 'Project'
        db.create_table('project_project_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['project.project'], null=False)),
            ('projectcategory', models.ForeignKey(orm['project.projectcategory'], null=False))
        ))
        db.create_unique('project_project_categories', ['project_id', 'projectcategory_id'])
        """

        # Adding model 'ProjectGratefulUsers'
        db.create_table('project_projectgratefulusers', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('project', ['ProjectGratefulUsers'])

        """
        # Adding model 'ProjectNeed'
        db.create_table('project_projectneed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('brief', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=12, decimal_places=0)),
            ('date_starting', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 14, 0, 0), null=True, blank=True)),
            ('date_ending', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 14, 0, 0))),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('project', ['ProjectNeed'])

        # Adding unique constraint on 'ProjectNeed', fields ['project', 'key']
        db.create_unique('project_projectneed', ['project_id', 'key'])
        """

        """
        # Adding model 'ProjectGoal'
        db.create_table('project_projectgoal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('brief', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('short_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('long_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('video_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=12, decimal_places=0)),
            ('date_starting', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 14, 0, 0))),
            ('date_ending', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 14, 0, 0))),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('project', ['ProjectGoal'])

        # Adding unique constraint on 'ProjectGoal', fields ['project', 'key']
        db.create_unique('project_projectgoal', ['project_id', 'key'])
        """

        """
        # Adding model 'Project_Dependencies'
        db.create_table('project_project_dependencies', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('depender_project', self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='depender', to=orm['project.Project'])),
            ('dependee_project', self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='dependee', to=orm['project.Project'])),
            ('brief', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('redonation_percent', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=2, decimal_places=0, blank=True)),
            ('redonation_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 14, 0, 0))),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('project', ['Project_Dependencies'])

        # Adding unique constraint on 'Project_Dependencies', fields ['depender_project', 'dependee_project']
        db.create_unique('project_project_dependencies', ['depender_project_id', 'dependee_project_id'])
        """

        """
        # Adding model 'ProjectOtherSource'
        db.create_table('project_projectothersource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('brief', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('is_monthly', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_received', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 14, 0, 0))),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('project', ['ProjectOtherSource'])
        """


    def backwards(self, orm):
        """
        # Removing unique constraint on 'Project_Dependencies', fields ['depender_project', 'dependee_project']
        db.delete_unique('project_project_dependencies', ['depender_project_id', 'dependee_project_id'])

        # Removing unique constraint on 'ProjectGoal', fields ['project', 'key']
        db.delete_unique('project_projectgoal', ['project_id', 'key'])

        # Removing unique constraint on 'ProjectNeed', fields ['project', 'key']
        db.delete_unique('project_projectneed', ['project_id', 'key'])

        # Deleting model 'ProjectCategory'
        db.delete_table('project_projectcategory')

        # Deleting model 'Project'
        db.delete_table('project_project')

        # Removing M2M table for field categories on 'Project'
        db.delete_table('project_project_categories')

        # Deleting model 'ProjectGratefulUsers'
        db.delete_table('project_projectgratefulusers')

        # Deleting model 'ProjectNeed'
        db.delete_table('project_projectneed')

        # Deleting model 'ProjectGoal'
        db.delete_table('project_projectgoal')

        # Deleting model 'Project_Dependencies'
        db.delete_table('project_project_dependencies')

        # Deleting model 'ProjectOtherSource'
        db.delete_table('project_projectothersource')
        """

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
            'brief': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.ProjectCategory']", 'symmetrical': 'False'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 14, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'maintainer_id': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': "orm['auth.User']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unclaimed'", 'max_length': '80'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.project_dependencies': {
            'Meta': {'unique_together': "(('depender_project', 'dependee_project'),)", 'object_name': 'Project_Dependencies'},
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 14, 0, 0)'}),
            'dependee_project': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'related_name': "'dependee'", 'to': "orm['project.Project']"}),
            'depender_project': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'related_name': "'depender'", 'to': "orm['project.Project']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'redonation_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'redonation_percent': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '2', 'decimal_places': '0', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'project.projectcategory': {
            'Meta': {'object_name': 'ProjectCategory'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 14, 0, 0)'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectgoal': {
            'Meta': {'unique_together': "(('project', 'key'),)", 'object_name': 'ProjectGoal'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '0'}),
            'brief': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 14, 0, 0)'}),
            'date_ending': ('django.db.models.fields.DateTimeField', [], {}),
            'date_starting': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 14, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'long_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'short_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'video_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'project.projectgratefulusers': {
            'Meta': {'object_name': 'ProjectGratefulUsers'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'project.projectneed': {
            'Meta': {'unique_together': "(('project', 'key'),)", 'object_name': 'ProjectNeed'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '0'}),
            'brief': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 14, 0, 0)'}),
            'date_ending': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_starting': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 14, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectothersource': {
            'Meta': {'object_name': 'ProjectOtherSource'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 14, 0, 0)'}),
            'date_received': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_monthly': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['project']