# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DonationCart'
        db.create_table('pledger_donationcart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('donation_type', self.gf('django.db.models.fields.CharField')(max_length=7)),
            ('datetime_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 10, 10, 15, 15, 57, 2))),
        ))
        db.send_create_signal('pledger', ['DonationCart'])

        # Adding model 'DonationSubscription'
        db.create_table('pledger_donationsubscription', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('datetime_last_sent', self.gf('django.db.models.fields.DateTimeField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('pledger', ['DonationSubscription'])

        # Adding model 'DonationHistory'
        db.create_table('pledger_donationhistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['project.Project'])),
            ('datetime_sent', self.gf('django.db.models.fields.DateTimeField')()),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('donation_subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pledger.DonationSubscription'], null=True, on_delete=models.SET_NULL)),
        ))
        db.send_create_signal('pledger', ['DonationHistory'])


    def backwards(self, orm):
        # Deleting model 'DonationCart'
        db.delete_table('pledger_donationcart')

        # Deleting model 'DonationSubscription'
        db.delete_table('pledger_donationsubscription')

        # Deleting model 'DonationHistory'
        db.delete_table('pledger_donationhistory')


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
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'datetime_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 10, 15, 15, 57, 2)'}),
            'donation_type': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pledger.donationhistory': {
            'Meta': {'object_name': 'DonationHistory'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'datetime_sent': ('django.db.models.fields.DateTimeField', [], {}),
            'donation_subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pledger.DonationSubscription']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'pledger.donationsubscription': {
            'Meta': {'object_name': 'DonationSubscription'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'datetime_last_sent': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['project.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'project.project': {
            'Meta': {'object_name': 'Project'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 10, 10, 15, 15, 57, 2)'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'maintainer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'regular_need': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '0', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['pledger']