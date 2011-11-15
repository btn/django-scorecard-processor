from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, update_object
from django.contrib.auth.decorators import login_required

from models import Entity, Project, Survey, Question, Scorecard, ReportRun
entity_qs = Entity.objects.all()
project_qs = Project.objects.all()
survey_qs = Survey.objects.all()
question_qs = Question.objects.all()
scorecard_qs = Scorecard.objects.all()
reportrun_qs = ReportRun.objects.all()

urlpatterns = patterns('scorecard_processor.views',
    url(r'^$', 'index', name="scorecard_index"),

#Projects, surveys and scorecards
#TODO:limit entities to the ones a user account can access
    url(r'^project/$', 
        login_required(object_list), 
        {'queryset':project_qs},
        name="project_list"
    ), 
    url(r'^project/(?P<object_id>\d+)/$', 
        login_required(object_detail),
        {'queryset':project_qs}, 
        name="show_project"
    ),

    url(r'^project/(\d+)/survey/(?P<object_id>\d+)/$', 
        login_required(object_detail),
        {'queryset': survey_qs}, 
        name="show_survey"
    ),

    url(r'^project/(\d+)/scorecard/(?P<object_id>\d+)/$',
        login_required(object_detail),
        {'queryset': scorecard_qs}, 
        name="show_scorecard"
    ),

    url(r'^project/(\d+)/report/(?P<object_id>\d+)/$',
        login_required(object_detail),
        {'queryset': reportrun_qs}, 
        name="show_report"
    ),
    url(r'^project/(\d+)/report/(?P<object_id>\d+)/run/$',
        login_required(object_detail),
        {'queryset': reportrun_qs,'template_name':'scorecard_processor/reportrun_run.html'}, 
        name="run_report"
    ),


#Response side
    url(r'^entity/$', #TODO:limit entities to the ones a user account can access
        login_required(object_list), 
        {'queryset':entity_qs},
        name="entity_list"
    ), 
    url(r'^entity/(?P<object_id>\d+)/$', 
        login_required(object_detail),
        {'queryset':entity_qs}, 
        name="show_entity"
    ),
    url(r'^entity/(?P<object_id>\d+)/survey/add/(?P<survey_id>\d+)/$','add_survey',name="survey_response"),
    #TODO: urls for responses per survey
    url(r'^entity/(?P<object_id>\d+)/response/(?P<responseset_id>\d+)/edit/$','edit_survey',name="survey_response_edit"),
)

