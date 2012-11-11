# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DonationCartNeeds'
        db.create_table('pledger_donationcartneeds', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('donation_cart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationCart'])),
            ('need', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.ProjectNeed'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('pledger', ['DonationCartNeeds'])

        # Adding model 'DonationSubscriptionNeeds'
        db.create_table('pledger_donationsubscriptionneeds', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('donation_subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationCart'])),
            ('need', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.ProjectNeed'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('pledger', ['DonationSubscriptionNeeds'])

        # Adding model 'DonationCartGoals'
        db.create_table('pledger_donationcartgoals', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('donation_cart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationCart'])),
            ('goal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.ProjectGoal'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('pledger', ['DonationCartGoals'])

        # Adding model 'DonationHistoryGoals'
        db.create_table('pledger_donationhistorygoals', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('donation_history', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationHistory'])),
            ('goal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.ProjectGoal'], null=True, on_delete=models.SET_NULL)),
            ('goal_title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('goal_key', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('goal_date_ending', self.gf('django.db.models.fields.DateField')()),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('pledger', ['DonationHistoryGoals'])

        # Adding model 'DonationHistoryNeeds'
        db.create_table('pledger_donationhistoryneeds', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('donation_history', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationHistory'])),
            ('need', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.ProjectNeed'], null=True, on_delete=models.SET_NULL)),
            ('need_title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('need_key', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=6, decimal_places=2)),
        ))
        db.send_create_signal('pledger', ['DonationHistoryNeeds'])

        # Deleting field 'DonationSubscription.amount'
        db.delete_column('pledger_donationsubscription', 'amount')

        # Deleting field 'DonationHistory.amount'
        db.delete_column('pledger_donationhistory', 'amount')

        # Adding field 'DonationHistory.username'
        db.add_column('pledger_donationhistory', 'username',
                      self.gf('django.db.models.fields.CharField')(max_length=30, null=True),
                      keep_default=False)

        # Adding field 'DonationHistory.project_title'
        db.add_column('pledger_donationhistory', 'project_title',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                      keep_default=False)

        # Adding field 'DonationHistory.project_key'
        db.add_column('pledger_donationhistory', 'project_key',
                      self.gf('django.db.models.fields.CharField')(max_length=80, null=True),
                      keep_default=False)

        # Adding field 'DonationHistory.donation_type'
        db.add_column('pledger_donationhistory', 'donation_type',
                      self.gf('django.db.models.fields.CharField')(default='onetime', max_length=7),
                      keep_default=False)


        # Changing field 'DonationHistory.project'
        db.alter_column('pledger_donationhistory', 'project_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'], null=True, on_delete=models.SET_NULL))

        # Changing field 'DonationHistory.user'
        db.alter_column('pledger_donationhistory', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL))
        # Deleting field 'DonationCart.amount'
        db.delete_column('pledger_donationcart', 'amount')


    def backwards(self, orm):
        # Deleting model 'DonationCartNeeds'
        db.delete_table('pledger_donationcartneeds')

        # Deleting model 'DonationSubscriptionNeeds'
        db.delete_table('pledger_donationsubscriptionneeds')

        # Deleting model 'DonationCartGoals'
        db.delete_table('pledger_donationcartgoals')

        # Deleting model 'DonationHistoryGoals'
        db.delete_table('pledger_donationhistorygoals')

        # Deleting model 'DonationHistoryNeeds'
        db.delete_table('pledger_donationhistoryneeds')

        # Adding field 'DonationSubscription.amount'
        db.add_column('pledger_donationsubscription', 'amount',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'DonationHistory.amount'
        db.add_column('pledger_donationhistory', 'amount',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'DonationHistory.username'
        db.delete_column('pledger_donationhistory', 'username')

        # Deleting field 'DonationHistory.project_title'
        db.delete_column('pledger_donationhistory', 'project_title')

        # Deleting field 'DonationHistory.project_key'
        db.delete_column('pledger_donationhistory', 'project_key')

        # Deleting field 'DonationHistory.donation_type'
        db.delete_column('pledger_donationhistory', 'donation_type')


        # User chose to not deal with backwards NULL issues for 'DonationHistory.project'
        raise RuntimeError("Cannot reverse this migration. 'DonationHistory.project' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'DonationHistory.user'
        raise RuntimeError("Cannot reverse this migration. 'DonationHistory.user' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'DonationCart.amount'
        raise RuntimeError("Cannot reverse this migration. 'DonationCart.amount' and its values cannot be restored.")

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
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 12, 14, 0, 3, 4)'}),
            'donation_type': ('django.db.models.fields.CharField', [], {'default': "'onetime'", 'max_length': '7'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pledger.donationcartgoals': {
            'Meta': {'object_name': 'DonationCartGoals'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'donation_cart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationCart']"}),
            'goal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectGoal']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'pledger.donationcartneeds': {
            'Meta': {'object_name': 'DonationCartNeeds'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'donation_cart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationCart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectNeed']"})
        },
        'pledger.donationhistory': {
            'Meta': {'object_name': 'DonationHistory'},
            'datetime_sent': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 12, 14, 0, 3, 4)'}),
            'donation_subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationSubscription']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'donation_type': ('django.db.models.fields.CharField', [], {'default': "'onetime'", 'max_length': '7'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'project_key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True'}),
            'project_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'})
        },
        'pledger.donationhistorygoals': {
            'Meta': {'object_name': 'DonationHistoryGoals'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'donation_history': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationHistory']"}),
            'goal': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectGoal']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'goal_date_ending': ('django.db.models.fields.DateField', [], {}),
            'goal_key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'goal_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'pledger.donationhistoryneeds': {
            'Meta': {'object_name': 'DonationHistoryNeeds'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'donation_history': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationHistory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectNeed']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'need_key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'need_title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'pledger.donationsubscription': {
            'Meta': {'object_name': 'DonationSubscription'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'datetime_last_sent': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pledger.donationsubscriptionneeds': {
            'Meta': {'object_name': 'DonationSubscriptionNeeds'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'donation_subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationCart']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'need': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.ProjectNeed']"})
        },
        'project.project': {
            'Meta': {'object_name': 'Project'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 12, 14, 0, 3, 4)'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'maintainer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'regular_need': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '0', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectgoal': {
            'Meta': {'object_name': 'ProjectGoal'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '0'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 12, 14, 0, 3, 4)'}),
            'date_ending': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'project.projectneed': {
            'Meta': {'object_name': 'ProjectNeed'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '0'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 12, 14, 0, 3, 4)'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['pledger']