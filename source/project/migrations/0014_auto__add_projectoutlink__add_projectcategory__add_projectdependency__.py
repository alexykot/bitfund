# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProjectOutlink'
        db.create_table('project_projectoutlink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 23, 13, 23, 38, 2))),
        ))
        db.send_create_signal('project', ['ProjectOutlink'])

        # Adding model 'ProjectCategory'
        db.create_table('project_projectcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 23, 13, 23, 38, 2))),
        ))
        db.send_create_signal('project', ['ProjectCategory'])

        # Adding model 'ProjectDependency'
        db.create_table('project_projectdependency', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('depending_project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='depending', to=orm['project.Project'])),
            ('depended_project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='depended', to=orm['project.Project'])),
            ('brief', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('redonation_percent', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=2, decimal_places=0, blank=True)),
            ('redonation_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 23, 13, 23, 38, 2))),
        ))
        db.send_create_signal('project', ['ProjectDependency'])

        # Adding model 'ProjectContact'
        db.create_table('project_projectcontact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 23, 13, 23, 38, 2))),
        ))
        db.send_create_signal('project', ['ProjectContact'])

        # Adding model 'ProjectOtherSource'
        db.create_table('project_projectothersource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('brief', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=2, blank=True)),
            ('is_monthly', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_received', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 23, 13, 23, 38, 2))),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('project', ['ProjectOtherSource'])

        # Adding field 'ProjectUserRole.date_added'
        db.add_column('project_projectuserrole', 'date_added',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 1, 23, 13, 23, 38, 2)),
                      keep_default=False)

        # Deleting field 'Project.description'
        db.delete_column('project_project', 'description')

        # Deleting field 'Project.other_sources'
        db.delete_column('project_project', 'other_sources')

        # Adding field 'Project.brief'
        db.add_column('project_project', 'brief',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Project.about'
        db.add_column('project_project', 'about',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Project.contribute'
        db.add_column('project_project', 'contribute',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding M2M table for field categories on 'Project'
        db.create_table('project_project_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('project', models.ForeignKey(orm['project.project'], null=False)),
            ('projectcategory', models.ForeignKey(orm['project.projectcategory'], null=False))
        ))
        db.create_unique('project_project_categories', ['project_id', 'projectcategory_id'])

        # Adding field 'ProjectGoal.brief'
        db.add_column('project_projectgoal', 'brief',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'ProjectGoal.image'
        db.add_column('project_projectgoal', 'image',
                      self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True),
                      keep_default=False)

        # Adding field 'ProjectGoal.video_url'
        db.add_column('project_projectgoal', 'video_url',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Adding field 'ProjectGoal.is_public'
        db.add_column('project_projectgoal', 'is_public',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


        # Changing field 'ProjectGoal.description'
        db.alter_column('project_projectgoal', 'description', self.gf('django.db.models.fields.TextField')(null=True))
        # Adding field 'ProjectNeed.is_public'
        db.add_column('project_projectneed', 'is_public',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ProjectOutlink'
        db.delete_table('project_projectoutlink')

        # Deleting model 'ProjectCategory'
        db.delete_table('project_projectcategory')

        # Deleting model 'ProjectDependency'
        db.delete_table('project_projectdependency')

        # Deleting model 'ProjectContact'
        db.delete_table('project_projectcontact')

        # Deleting model 'ProjectOtherSource'
        db.delete_table('project_projectothersource')

        # Deleting field 'ProjectUserRole.date_added'
        db.delete_column('project_projectuserrole', 'date_added')

        # Adding field 'Project.description'
        db.add_column('project_project', 'description',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Project.other_sources'
        db.add_column('project_project', 'other_sources',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=0, blank=True),
                      keep_default=False)

        # Deleting field 'Project.brief'
        db.delete_column('project_project', 'brief')

        # Deleting field 'Project.about'
        db.delete_column('project_project', 'about')

        # Deleting field 'Project.contribute'
        db.delete_column('project_project', 'contribute')

        # Removing M2M table for field categories on 'Project'
        db.delete_table('project_project_categories')

        # Deleting field 'ProjectGoal.brief'
        db.delete_column('project_projectgoal', 'brief')

        # Deleting field 'ProjectGoal.image'
        db.delete_column('project_projectgoal', 'image')

        # Deleting field 'ProjectGoal.video_url'
        db.delete_column('project_projectgoal', 'video_url')

        # Deleting field 'ProjectGoal.is_public'
        db.delete_column('project_projectgoal', 'is_public')


        # Changing field 'ProjectGoal.description'
        db.alter_column('project_projectgoal', 'description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))
        # Deleting field 'ProjectNeed.is_public'
        db.delete_column('project_projectneed', 'is_public')


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
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 13, 23, 38, 2)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectcategory': {
            'Meta': {'object_name': 'ProjectCategory'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 13, 23, 38, 2)'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectcontact': {
            'Meta': {'object_name': 'ProjectContact'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 13, 23, 38, 2)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'project.projectdependency': {
            'Meta': {'object_name': 'ProjectDependency'},
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 13, 23, 38, 2)'}),
            'depended_project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'depended'", 'to': "orm['project.Project']"}),
            'depending_project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'depending'", 'to': "orm['project.Project']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redonation_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'redonation_percent': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '2', 'decimal_places': '0', 'blank': 'True'})
        },
        'project.projectgoal': {
            'Meta': {'object_name': 'ProjectGoal'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '0'}),
            'brief': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 13, 23, 38, 2)'}),
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
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 13, 23, 38, 2)'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectothersource': {
            'Meta': {'object_name': 'ProjectOtherSource'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 13, 23, 38, 2)'}),
            'date_received': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_monthly': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectoutlink': {
            'Meta': {'object_name': 'ProjectOutlink'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 13, 23, 38, 2)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'project.projectuserrole': {
            'Meta': {'object_name': 'ProjectUserRole'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 1, 23, 13, 23, 38, 2)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.Profile']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user_role': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'user_role_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['project']