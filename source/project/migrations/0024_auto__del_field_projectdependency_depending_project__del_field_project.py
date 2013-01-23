# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ProjectDependency.depending_project'
        db.delete_column('project_projectdependency', 'depending_project_id')

        # Deleting field 'ProjectDependency.depended_project'
        db.delete_column('project_projectdependency', 'depended_project_id')

        # Adding field 'ProjectDependency.idependon_project'
        db.add_column('project_projectdependency', 'idependon_project',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=3, related_name='idependon', to=orm['project.Project']),
                      keep_default=False)

        # Adding field 'ProjectDependency.dependonme_project'
        db.add_column('project_projectdependency', 'dependonme_project',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=0, related_name='dependonme', to=orm['project.Project']),
                      keep_default=False)

        # Adding field 'ProjectDependency.is_public'
        db.add_column('project_projectdependency', 'is_public',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'ProjectDependency.sort_order'
        db.add_column('project_projectdependency', 'sort_order',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'ProjectContact.is_public'
        db.add_column('project_projectcontact', 'is_public',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'ProjectContact.sort_order'
        db.add_column('project_projectcontact', 'sort_order',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'ProjectDependency.depending_project'
        raise RuntimeError("Cannot reverse this migration. 'ProjectDependency.depending_project' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'ProjectDependency.depended_project'
        raise RuntimeError("Cannot reverse this migration. 'ProjectDependency.depended_project' and its values cannot be restored.")
        # Deleting field 'ProjectDependency.idependon_project'
        db.delete_column('project_projectdependency', 'idependon_project_id')

        # Deleting field 'ProjectDependency.dependonme_project'
        db.delete_column('project_projectdependency', 'dependonme_project_id')

        # Deleting field 'ProjectDependency.is_public'
        db.delete_column('project_projectdependency', 'is_public')

        # Deleting field 'ProjectDependency.sort_order'
        db.delete_column('project_projectdependency', 'sort_order')

        # Deleting field 'ProjectContact.is_public'
        db.delete_column('project_projectcontact', 'is_public')

        # Deleting field 'ProjectContact.sort_order'
        db.delete_column('project_projectcontact', 'sort_order')


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
        'pledger.profile': {
            'Meta': {'object_name': 'Profile'},
            'bitbucket_profile': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'github_profile': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'registered'", 'max_length': '15'}),
            'sourceforge_profile': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'my_profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'project.project': {
            'Meta': {'object_name': 'Project'},
            'about': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'brief': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.ProjectCategory']", 'symmetrical': 'False'}),
            'contribute': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 17, 38, 56, 2)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectcategory': {
            'Meta': {'object_name': 'ProjectCategory'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 17, 38, 56, 2)'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectcontact': {
            'Meta': {'object_name': 'ProjectContact'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 17, 38, 56, 2)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'project.projectdependency': {
            'Meta': {'object_name': 'ProjectDependency'},
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 17, 38, 56, 2)'}),
            'dependonme_project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dependonme'", 'to': "orm['project.Project']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idependon_project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'idependon'", 'to': "orm['project.Project']"}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'redonation_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'redonation_percent': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '2', 'decimal_places': '0', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'project.projectgoal': {
            'Meta': {'object_name': 'ProjectGoal'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '0'}),
            'brief': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 17, 38, 56, 2)'}),
            'date_ending': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'video_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'project.projectneed': {
            'Meta': {'object_name': 'ProjectNeed'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '0'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 17, 38, 56, 2)'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectothersource': {
            'Meta': {'object_name': 'ProjectOtherSource'},
            'amount_percent': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '0', 'blank': 'True'}),
            'amount_sum': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 17, 38, 56, 2)'}),
            'date_received': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_monthly': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectoutlink': {
            'Meta': {'object_name': 'ProjectOutlink'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 17, 38, 56, 2)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'project.projectrelease': {
            'Meta': {'object_name': 'ProjectRelease'},
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 17, 38, 56, 2)'}),
            'date_released': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'previous_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectRelease']", 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'project.projectuserrole': {
            'Meta': {'object_name': 'ProjectUserRole'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 17, 38, 56, 2)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.Profile']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user_role': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'user_role_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['project']