from datetime import datetime, timedelta

from django.db import models
from django.db.models.query import QuerySet, Q
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from cerial import PickleField, JSONField

from inputs import Survey, ResponseSet
from meta import DataSeriesGroup, DataSeries, Project, Entity, EntityType

from scorecard_processor import plugins

class Scorecard(models.Model):
    """Could have multiple transformations grouped for the same 'output', e.g.
    government score card, Country scorecard, 2011 scorecard"""
    name = models.CharField(max_length=50)
    project = models.ForeignKey(Project)

    class Meta:
        app_label = "scorecard_processor"

    def __unicode__(self):
        return "Scorecard: %s" % (self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('show_scorecard',(str(self.project.pk),str(self.pk)))

    def get_values(self, responsesets, group_by = None):
        result = []
        #TODO: this is going to break with hierachy
        for indicator in self.operation_set.filter(indicator=True):
            result.append((indicator, indicator.get_data(responsesets)))
        return result

class OperationManager(models.Manager):
    def indicators(self):
        return self.filter(indicator=True)

class Operation(models.Model):
    """Methods are grouped by how they slice data 
    - per ResponseSet
    - per DataSet
    """
    #TODO: validate number of arguments
    #TODO: validate argument positions
    #TODO: operations should be chained? e.g. div(sum(Q1),sum(Q2)) vs. NumDenom(Q1,Q2)
    #TODO: rework as django-mptt?
    scorecard = models.ForeignKey(Scorecard)
    operation = models.CharField(max_length=50, choices=plugins.process_plugins_as_choices(), help_text="How should this data be processed") 
    identifier = models.CharField(max_length=25, help_text="A short identifier for the operation, e.g. budget_spend, 1G")
    description = models.CharField(max_length=200, help_text="Descriptive name for this indicator e.g. Portion of budget spent(%), Total amount spent ($m)")
    configuration = JSONField(null=True, blank=True) #For the case of creating check mark outputs
    indicator = models.BooleanField(default=False, help_text="Is this an output operation, or a pre-cursor to output?")
    objects = OperationManager()

    class Meta:
        app_label = "scorecard_processor"
        ordering = ('identifier',)

    def __init__(self, *args, **kwargs):
        super(Operation,self).__init__(*args, **kwargs)
        if self.operation:
            self.plugin = plugins.register.get_process_plugin(self.operation).plugin
        else:
            self.plugin = None

    def __unicode__(self):
        return "%s: %s" % (self.identifier, self.get_operation_display())

    def get_data(self, responsesets):
        """ Outputs a value from the operation, applying the method to the
        arguments"""
        fetched_rs = [rs for rs in responsesets]
        key = reduce(lambda x,y: x^y, [rs.pk for rs in fetched_rs])
        latest = fetched_rs[0].last_update
        try:
            result = get_cached_result(self, data_hash = key, latest_item = latest)
        except NoCachedResult:
            result = self.plugin(self, responsesets).process()
            set_cached_result(self, data_hash = key, latest_item = latest, data=result)
        return result


        
class OperationArgument(models.Model):
    """Arguments need to be ordered and they may be specific question
    responses, or outputs from transitions""" 

    position = models.IntegerField(default=0, db_index=True)
    operation = models.ForeignKey(Operation)
    instance_content_type = models.ForeignKey(ContentType)
    instance_id = models.PositiveIntegerField()
    instance = generic.GenericForeignKey('instance_content_type', 'instance_id')
    argument_extractor = models.CharField(max_length=30, default='value') #argument / sub-type / how to tease out value. Based on instance type...

    class Meta:
        app_label = "scorecard_processor"
        ordering = ('position',)
        unique_together = ('position','operation')

    def __unicode__(self):
        return u"%s: %s" % (self.operation.plugin.argument_list[self.position], self.instance) 

    def get_data(self, responsesets, latest=None):
        response = self.instance.get_data(responsesets)
        if isinstance(response, QuerySet):
            response = plugins.Vector(response)
        return response

        
"""

Scorecard from 2010 submissions from South Africa, Nigeria, Somalia
    aggregated by country

Scorecard for 2009 submissions from South Africa, for USAID, WHO
    aggregated by entity

Scorecard for 2009 and 2010 for all countries
    aggregated by entity

"""

class ReportRunError(Exception):
    pass

class ReportRun(models.Model):
    scorecard = models.ForeignKey(Scorecard)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    #Need one or both methods of aggregation
    aggregate_on = models.ForeignKey(DataSeriesGroup, blank=True, null=True)
    aggregate_by_entity = models.BooleanField(default=False)

    #Optional filters for underlying responsesets
    limit_to_dataseries = models.ManyToManyField(DataSeries, blank=True, null=True) #Optionally limit to dataseries
    limit_to_entity = models.ManyToManyField(Entity, blank=True, null=True) #Optionally limit to entities
    limit_to_entitytype = models.ManyToManyField(EntityType, blank=True, null=True) #Optionally limit to entity types

    class Meta:
        app_label = "scorecard_processor"

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('show_report',(str(self.scorecard.project.pk),str(self.pk)))

    def get_responsesets(self):
        if not self.aggregate_by_entity and not self.aggregate_on:
            raise ReportRunError("No aggregation mode selected")

        qs = ResponseSet.objects.filter(survey__project__pk=self.scorecard.project.pk)
        
        if self.limit_to_dataseries.count():
            qs = qs.filter(data_series__in=self.limit_to_dataseries.all())

        if self.limit_to_entity.count():
            qs = qs.filter(entity__in=self.limit_to_entity.all())

        if self.limit_to_entitytype.count():
            qs = qs.filter(entity__entity_type__in=self.limit_to_entitytype.all())

        qs = qs.only('id','last_update')
        rs_dict = {}

        if self.aggregate_on:
            for dataseries in self.aggregate_on.dataseries_set.all():
                ds_qs = qs.filter(data_series=dataseries)
                if ds_qs.count():
                    if self.aggregate_by_entity:
                        for entity in self.scorecard.project.entity_set.all():
                            e_qs = ds_qs.filter(entity=entity)
                            if e_qs.count():
                                rs_dict[entity] = rs_dict.get(entity, {})
                                rs_dict[entity][dataseries] = e_qs
                    else:
                        rs_dict[dataseries] = ds_qs
        else:
            for entity in self.scorecard.project.entity_set.all():
                e_qs = qs.filter(entity=entity)
                if e_qs.count():
                    rs_dict[entity] = e_qs
        return rs_dict

    def run(self):
        results = {}
        #TODO: don't hardcore... figure out how to get scorecard data
        scorecard = Scorecard.objects.get(pk=1)
        for key, qs in self.get_responsesets().items():
            if isinstance(qs, QuerySet):
                results[key] = scorecard.get_values(qs)
            else:
                results[key] = plugins.Vector([(k, scorecard.get_values(q)) for k,q in qs.items()])
        return results

def default_expires(*args, **kwargs):
    return datetime.now() + timedelta(days=5)

class CachedResult(models.Model):
    operation = models.ForeignKey(Operation)

    data_hash = models.IntegerField(db_index=True)
    data = PickleField()

    latest_item = models.DateTimeField()
    expires = models.DateTimeField(default=default_expires)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "scorecard_processor"

class NoCachedResult(Exception):
    pass

def get_cached_result(operation, data_hash, latest_item):
    result = None
    try:
        result = operation.cachedresult_set.get(data_hash = data_hash, latest_item = latest_item).data
    except CachedResult.DoesNotExist:
        raise NoCachedResult
    return result

def set_cached_result(operation, data_hash, latest_item, data):
    cache = operation.cachedresult_set.create(data_hash = data_hash, latest_item = latest_item)
    cache.data = data
    cache.save()
