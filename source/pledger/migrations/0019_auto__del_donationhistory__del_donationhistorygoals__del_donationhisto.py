# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'DonationHistory'
        db.delete_table('pledger_donationhistory')

        # Deleting model 'DonationHistoryGoals'
        db.delete_table('pledger_donationhistorygoals')

        # Deleting model 'DonationHistoryNeeds'
        db.delete_table('pledger_donationhistoryneeds')

        # Adding model 'DonationTransactionGoals'
        db.create_table('pledger_donationtransactiongoals', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('donation_history', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationTransaction'])),
            ('goal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.ProjectGoal'], null=True, on_delete=models.SET_NULL)),
            ('goal_title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('goal_key', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('goal_date_ending', self.gf('django.db.models.fields.DateField')()),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=12, decimal_places=2)),
        ))
        db.send_create_signal('pledger', ['DonationTransactionGoals'])

        # Adding model 'DonationTransactionDetails'
        db.create_table('pledger_donationtransactiondetails', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('donation_transaction', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['pledger.DonationTransaction'], unique=True)),
            ('pledge_username', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('pledge_email', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('other_source_title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('redonation_project_key', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('redonation_project_title', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
        ))
        db.send_create_signal('pledger', ['DonationTransactionDetails'])

        # Adding model 'DonationTransaction'
        db.create_table('pledger_donationtransaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transaction_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('transaction_hash', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('pledge_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('pledge_donation_subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationSubscription'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('redonation_transaction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationTransaction'], null=True, on_delete=models.PROTECT, blank=True)),
            ('redonation_project', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='redonation_project', null=True, on_delete=models.SET_NULL, to=orm['project.Project'])),
            ('accepting_project', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='accepting_project', null=True, on_delete=models.SET_NULL, to=orm['project.Project'])),
            ('accepting_project_key', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('accepting_project_title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('datetime_sent', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 8, 0, 0))),
        ))
        db.send_create_signal('pledger', ['DonationTransaction'])

        # Adding model 'DonationTransactionNeeds'
        db.create_table('pledger_donationtransactionneeds', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('donation_history', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationTransaction'])),
            ('need', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.ProjectNeed'], null=True, on_delete=models.SET_NULL)),
            ('need_title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('need_key', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=12, decimal_places=2)),
            ('donation_type', self.gf('django.db.models.fields.CharField')(default='onetime', max_length=7)),
        ))
        db.send_create_signal('pledger', ['DonationTransactionNeeds'])

        # Deleting field 'Profile.token'
        db.delete_column('pledger_profile', 'token')

        # Adding field 'Profile.api_token'
        db.add_column('pledger_profile', 'api_token',
                      self.gf('django.db.models.fields.CharField')(default='aasd', unique=True, max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Adding model 'DonationHistory'
        db.create_table('pledger_donationhistory', (
            ('username', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('project_key', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('donation_subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationSubscription'], null=True, on_delete=models.SET_NULL)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('datetime_sent', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 4, 0, 0))),
            ('project_title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'], null=True, on_delete=models.SET_NULL)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL)),
        ))
        db.send_create_signal('pledger', ['DonationHistory'])

        # Adding model 'DonationHistoryGoals'
        db.create_table('pledger_donationhistorygoals', (
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=12, decimal_places=2)),
            ('goal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.ProjectGoal'], null=True, on_delete=models.SET_NULL)),
            ('goal_key', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('goal_date_ending', self.gf('django.db.models.fields.DateField')()),
            ('goal_title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('donation_history', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationHistory'])),
        ))
        db.send_create_signal('pledger', ['DonationHistoryGoals'])

        # Adding model 'DonationHistoryNeeds'
        db.create_table('pledger_donationhistoryneeds', (
            ('need_key', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=12, decimal_places=2)),
            ('donation_type', self.gf('django.db.models.fields.CharField')(default='onetime', max_length=7)),
            ('need_title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('need', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.ProjectNeed'], null=True, on_delete=models.SET_NULL)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('donation_history', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationHistory'])),
        ))
        db.send_create_signal('pledger', ['DonationHistoryNeeds'])

        # Deleting model 'DonationTransactionGoals'
        db.delete_table('pledger_donationtransactiongoals')

        # Deleting model 'DonationTransactionDetails'
        db.delete_table('pledger_donationtransactiondetails')

        # Deleting model 'DonationTransaction'
        db.delete_table('pledger_donationtransaction')

        # Deleting model 'DonationTransactionNeeds'
        db.delete_table('pledger_donationtransactionneeds')


        # User chose to not deal with backwards NULL issues for 'Profile.token'
        raise RuntimeError("Cannot reverse this migration. 'Profile.token' and its values cannot be restored.")
        # Deleting field 'Profile.api_token'
        db.delete_column('pledger_profile', 'api_token')


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
        'pledger.donationcart': {
            'Meta': {'object_name': 'DonationCart'},
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 8, 0, 0)'}),
            'goals': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.ProjectGoal']", 'through': "orm['pledger.DonationCartGoals']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'needs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.ProjectNeed']", 'through': "orm['pledger.DonationCartNeeds']", 'symmetrical': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pledger.donationcartgoals': {
            'Meta': {'object_name': 'DonationCartGoals'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2'}),
            'donation_cart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationCart']"}),
            'goal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectGoal']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'pledger.donationcartneeds': {
            'Meta': {'object_name': 'DonationCartNeeds'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2'}),
            'donation_cart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationCart']"}),
            'donation_type': ('django.db.models.fields.CharField', [], {'default': "'monthly'", 'max_length': '7'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectNeed']"})
        },
        'pledger.donationsubscription': {
            'Meta': {'object_name': 'DonationSubscription'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'datetime_last_sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'needs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.ProjectNeed']", 'through': "orm['pledger.DonationSubscriptionNeeds']", 'symmetrical': 'False'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pledger.donationsubscriptionneeds': {
            'Meta': {'object_name': 'DonationSubscriptionNeeds'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'donation_subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationSubscription']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectNeed']"})
        },
        'pledger.donationtransaction': {
            'Meta': {'object_name': 'DonationTransaction'},
            'accepting_project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'accepting_project'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['project.Project']"}),
            'accepting_project_key': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'accepting_project_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'datetime_sent': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 8, 0, 0)'}),
            'goals': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.ProjectGoal']", 'through': "orm['pledger.DonationTransactionGoals']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'needs': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.ProjectNeed']", 'through': "orm['pledger.DonationTransactionNeeds']", 'symmetrical': 'False'}),
            'pledge_donation_subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationSubscription']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'pledge_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'redonation_project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'redonation_project'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['project.Project']"}),
            'redonation_transaction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationTransaction']", 'null': 'True', 'on_delete': 'models.PROTECT', 'blank': 'True'}),
            'transaction_hash': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'transaction_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'pledger.donationtransactiondetails': {
            'Meta': {'object_name': 'DonationTransactionDetails'},
            'donation_transaction': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['pledger.DonationTransaction']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'other_source_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pledge_email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pledge_username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'redonation_project_key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'redonation_project_title': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'})
        },
        'pledger.donationtransactiongoals': {
            'Meta': {'object_name': 'DonationTransactionGoals'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2'}),
            'donation_history': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationTransaction']"}),
            'goal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectGoal']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'goal_date_ending': ('django.db.models.fields.DateField', [], {}),
            'goal_key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'goal_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'pledger.donationtransactionneeds': {
            'Meta': {'object_name': 'DonationTransactionNeeds'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '2'}),
            'donation_history': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationTransaction']"}),
            'donation_type': ('django.db.models.fields.CharField', [], {'default': "'onetime'", 'max_length': '7'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectNeed']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'need_key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'need_title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'pledger.profile': {
            'Meta': {'object_name': 'Profile'},
            'api_token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'donation_is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mugshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'registered'", 'max_length': '15'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'my_profile'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'project.project': {
            'Meta': {'object_name': 'Project'},
            'brief': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['project.ProjectCategory']", 'symmetrical': 'False'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 8, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectcategory': {
            'Meta': {'object_name': 'ProjectCategory'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 8, 0, 0)'}),
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
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 8, 0, 0)'}),
            'date_ending': ('django.db.models.fields.DateTimeField', [], {}),
            'date_starting': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 8, 0, 0)'}),
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
        'project.projectneed': {
            'Meta': {'unique_together': "(('project', 'key'),)", 'object_name': 'ProjectNeed'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '0'}),
            'brief': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 8, 0, 0)'}),
            'date_ending': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_starting': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 8, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['pledger']