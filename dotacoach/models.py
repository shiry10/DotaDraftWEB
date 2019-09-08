# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class NameId(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    name = models.TextField(db_column='NAME', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'NAME_ID'
        unique_together = (('id', 'name'),)


class WinrateOne(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    op = models.IntegerField(db_column='OP')
    winrate = models.FloatField(db_column='WINRATE')

    class Meta:
        managed = False
        db_table = 'WINRATE_ONE'
        unique_together = (('id', 'op'),)


class WinrateSingle(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    winrate = models.FloatField(db_column='WINRATE')

    class Meta:
        managed = False
        db_table = 'WINRATE_SINGLE'
