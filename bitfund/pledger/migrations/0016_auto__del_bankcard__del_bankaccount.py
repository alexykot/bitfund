# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'BankCard'
        db.delete_table('pledger_bankcard')

        # Deleting model 'BankAccount'
        db.delete_table('pledger_bankaccount')


    def backwards(self, orm):
        # Adding model 'BankCard'
        db.create_table('pledger_bankcard', (
            ('name_on_card', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('brand', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('last_four_digits', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('country_code', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('is_valid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('address_1', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('address_2', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('pledger', ['BankCard'])

        # Adding model 'BankAccount'
        db.create_table('pledger_bankaccount', (
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
        ))
        db.send_create_signal('pledger', ['BankAccount'])


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
        'pledger.donationsubscription': {
            'Meta': {'object_name': 'DonationSubscription'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '2'}),
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 4, 11, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'needs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.ProjectNeed']", 'through': "orm['pledger.DonationSubscriptionNeeds']", 'symmetrical': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pledger.donationsubscriptionneeds': {
            'Meta': {'object_name': 'DonationSubscriptionNeeds'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '2'}),
            'donation_subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationSubscription']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectNeed']"})
        },
        'pledger.donationtransaction': {
            'Meta': {'object_name': 'DonationTransaction'},
            'accepting_goal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectGoal']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'accepting_goal_datetime_ending': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'accepting_goal_key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'accepting_goal_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'accepting_need': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectNeed']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'accepting_need_key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'accepting_need_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'accepting_project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'accepting_project'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['project.Project']"}),
            'accepting_project_key': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'accepting_project_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'other_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectOtherSource']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'other_source_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pledger_donation_subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationSubscription']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'pledger_donation_type': ('django.db.models.fields.CharField', [], {'default': "'onetime'", 'max_length': '7', 'null': 'True', 'blank': 'True'}),
            'pledger_email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pledger_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'pledger_username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'redonation_project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'redonation_project'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['project.Project']"}),
            'redonation_project_key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'redonation_project_title': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'redonation_transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationTransaction']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'transaction_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2'}),
            'transaction_datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'transaction_hash': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'transaction_status': ('django.db.models.fields.CharField', [], {'default': "'unpaid'", 'max_length': '64'}),
            'transaction_type': ('django.db.models.fields.CharField', [], {'default': "'pledge'", 'max_length': '64'})
        },
        'pledger.profile': {
            'Meta': {'object_name': 'Profile', '_ormbases': ['auth.User']},
            'api_token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'donation_amount_is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'gravatar_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'projects_list_is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'twitter_pic_url': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['auth.User']"})
        },
        'project.project': {
            'Meta': {'object_name': 'Project'},
            'brief': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.ProjectCategory']", 'symmetrical': 'False'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 4, 11, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_maintainer_confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_refused_to_give_to_bitfund': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'maintainer': ('django.db.models.fields.related.ForeignKey', [], {'default': '-1', 'to': "orm['auth.User']", 'on_delete': 'models.PROTECT'}),
            'maintainer_reason_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'maintainer_reason_url': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'maintainer_status': ('django.db.models.fields.CharField', [], {'default': "'sole_developer'", 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unclaimed'", 'max_length': '80'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectcategory': {
            'Meta': {'object_name': 'ProjectCategory'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 4, 11, 0, 0)'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectgoal': {
            'Meta': {'unique_together': "(('project', 'key'),)", 'object_name': 'ProjectGoal'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '0'}),
            'brief': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 4, 11, 0, 0)'}),
            'date_ending': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_starting': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'vimeo_video_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'youtube_video_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'project.projectneed': {
            'Meta': {'unique_together': "(('project', 'key'),)", 'object_name': 'ProjectNeed'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '0', 'blank': 'True'}),
            'brief': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 4, 11, 0, 0)'}),
            'date_ending': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_starting': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 4, 11, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'project.projectothersource': {
            'Meta': {'object_name': 'ProjectOtherSource'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '2', 'blank': 'True'}),
            'brief': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 4, 11, 0, 0)'}),
            'date_received': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_monthly': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['pledger']