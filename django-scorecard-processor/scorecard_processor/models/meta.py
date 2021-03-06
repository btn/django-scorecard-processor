from django.db import models
from django.contrib.auth.models import User
from django.utils import translation


class Project(models.Model):
    name = models.CharField(max_length=100) 
    class Meta:
        app_label = "scorecard_processor"
        permissions = (
                        ("can_view", "Can view the project"),
                    )

    def _as_dict(self):
        return {'name':self.name}

    @models.permalink
    def get_absolute_url(self):
        return ('show_project',[str(self.pk)])

    def __unicode__(self):
        return "Project: %s" % (self.name)

    def get_report_links(self):
        from scorecard_processor import reports
        links = []
        for name, report in reports.get_project_reports():
            links.extend(report().get_report_links(self))
        return links

    def get_glossary(self):
        lang = translation.get_language()
        return GlossaryTerm.objects.filter(definition__lang=lang).select_related('definition')
        

class GlossaryDefinition(models.Model):
    project = models.ForeignKey(Project)
    definition = models.TextField() 
    lang = models.CharField(max_length=5, db_index=True)
    class Meta:
        app_label = "scorecard_processor"

    def __unicode__(self):
        return ", ".join([t.term for t in self.glossaryterm_set.all()] or [self.definition[:10]+'...'])

class GlossaryTerm(models.Model):
    term = models.CharField(max_length=200)
    definition = models.ForeignKey(GlossaryDefinition)
    class Meta:
        app_label = "scorecard_processor"

    def __unicode__(self):
        return self.term

# WIP for db based cache of which objects/fields need translation
#class GlossaryCache(models.Model):
#    obj = Generic...
#    term_set = ManyToManyField(GlossaryTerm)


class DataSeriesGroup(models.Model):
    name = models.CharField(max_length=30,primary_key=True)
    project = models.ForeignKey(Project)
    reverse_ordering = models.BooleanField(default=False)
    class Meta:
        ordering = ('name',)
        app_label = "scorecard_processor"

    def _as_dict(self):
        return {'name':self.name}

    def get_dataseries(self):
        qs = self.dataseries_set.filter(visible=True)
        if self.reverse_ordering:
            qs = qs.order_by('-name')
        return qs


    def __unicode__(self):
        return self.name

class DataSeries(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(DataSeriesGroup)
    visible = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Data Series'
        ordering = ('-group','name')
        app_label = "scorecard_processor"
        permissions = (
                        ("can_use", "Can use the DataSeries"),
                        ("can_view", "Can view the DataSeries"),
                    )

    def _as_dict(self):
        return {'name':self.name}

    @property
    def data_type(self):
        return self.group_id

    def __unicode__(self):
        return "%s: %s" % (self.group.pk, self.name)

class EntityType(models.Model):
    name = models.CharField(max_length=30,primary_key=True)
    plural = models.CharField(max_length=30)
    project = models.ForeignKey(Project)
    class Meta:
        app_label = "scorecard_processor"
    def __unicode__(self):
        return "%s / %s" % (self.name, self.plural)


class Entity(models.Model):
    """
    An entity / organisation
    """
    name = models.CharField(max_length=100) 
    abbreviation = models.CharField(max_length=30, blank=True, null=True)
    entity_type = models.ForeignKey(EntityType)
    project = models.ForeignKey(Project)

    class Meta:
        app_label = "scorecard_processor"
        unique_together = (('name','project'),)
        ordering = ('entity_type','name')
        permissions = (
                        ("can_view", "Can view the Entity"),
                    )

    def _as_dict(self):
        return {
                'name':self.name,
                'abbreviation':self.abbreviation,
                'entity_type':self.entity_type_id,
            }

    @property
    def data_type(self):
        return self.entity_type.pk

    def get_response_set(self, survey, data_series):
        qs = self.responseset_set.filter(survey=survey)
        for ds in data_series:
            qs = qs.filter(data_series=ds)
        if len(qs) == 0:
            return None
        if len(qs) == 1:
            return qs[0]
        return qs

    @models.permalink
    def get_absolute_url(self):
        return ('show_entity',(str(self.pk),))

    def get_report_links(self):
        from scorecard_processor import reports
        links = []
        for name, report in reports.get_entity_reports():
            links.extend(report().get_report_links(self))
        return links

    def __unicode__(self):
        if self.abbreviation:
            return "%s: %s (%s)" % (self.entity_type.pk.capitalize(), self.name, self.abbreviation)
        return "%s: %s" % (self.entity_type.pk.capitalize(), self.name)

